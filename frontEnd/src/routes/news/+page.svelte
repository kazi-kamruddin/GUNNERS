<script lang="ts">
	import { replaceState } from '$app/navigation';
	import { page } from '$app/state';
	import { untrack } from 'svelte';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { fetchArsenalNewsResult } from '$lib/api/football';
	import type { NewsItem } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const PAGE_SIZE = 12;

	let articles = $state<NewsItem[]>(untrack(() => data.feed?.articles ?? []));
	let total = $state<number>(untrack(() => data.feed?.total ?? 0));
	let hasMore = $state<boolean>(untrack(() => Boolean(data.feed?.has_more)));
	let sourcesActive = $state<string[]>(untrack(() => data.feed?.sources_active ?? []));
	let apiError = $state<string | null>(untrack(() => data.apiError ?? null));
	let selectedCategory = $state<string>(untrack(() => data.category || 'all'));
	let selectedTag = $state<string>(untrack(() => data.tag || 'all'));
	let searchQuery = $state<string>(untrack(() => data.search || ''));
	let isRefreshing = $state<boolean>(false);
	let isFiltering = $state<boolean>(false);
	let isLoadingMore = $state<boolean>(false);
	let failedImages = $state<Record<string, boolean>>({});
	let sentinelEl = $state<HTMLDivElement | null>(null);
	let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;
	let requestSeq = 0;

	let refreshBtnText = $derived(isRefreshing ? 'Syncing…' : 'Sync feeds');
	let loadMoreLabel = $derived(isLoadingMore ? 'Loading more…' : 'Load more dispatches');
	let hasActiveFilters = $derived(
		selectedCategory !== 'all' || selectedTag !== 'all' || searchQuery.trim().length > 0
	);

	$effect(() => {
		articles = data.feed?.articles ?? [];
		total = data.feed?.total ?? articles.length;
		hasMore = Boolean(data.feed?.has_more);
		sourcesActive = data.feed?.sources_active ?? [];
		apiError = data.apiError ?? null;
		selectedCategory = data.category || 'all';
		selectedTag = data.tag || 'all';
		searchQuery = data.search || '';
		failedImages = {};
	});

	const categories = [
		{ id: 'all', label: 'All updates' },
		{ id: 'fan_blog', label: 'Fan blogs' },
		{ id: 'reddit', label: 'r/Gunners top week' },
		{ id: 'broadcast', label: 'Broadcast (BBC Sport)' }
	];

	const quickTags = [
		'All',
		'Arteta',
		'Saka',
		'Ødegaard',
		'Saliba',
		'Rice',
		'Tactics',
		'UCL',
		'Premier League',
		'Transfers'
	];

	function syncNewsUrl() {
		if (typeof window === 'undefined') return;
		const nextUrl = new URL(page.url.href);
		if (selectedCategory && selectedCategory !== 'all') nextUrl.searchParams.set('category', selectedCategory);
		else nextUrl.searchParams.delete('category');
		if (selectedTag && selectedTag !== 'all') nextUrl.searchParams.set('tag', selectedTag);
		else nextUrl.searchParams.delete('tag');
		if (searchQuery.trim()) nextUrl.searchParams.set('search', searchQuery.trim());
		else nextUrl.searchParams.delete('search');
		replaceState(nextUrl, {});
	}

	async function reloadFeed(opts: { refresh?: boolean } = {}) {
		const seq = ++requestSeq;
		isFiltering = true;
		syncNewsUrl();
		try {
			const res = await fetchArsenalNewsResult({
				limit: PAGE_SIZE,
				offset: 0,
				category: selectedCategory,
				tag: selectedTag,
				search: searchQuery,
				refresh: Boolean(opts.refresh)
			});
			if (seq !== requestSeq) return;
			apiError = res.error;
			if (!res.error) {
				articles = res.data.articles ?? [];
				total = res.data.total ?? articles.length;
				hasMore = Boolean(res.data.has_more);
				sourcesActive = res.data.sources_active ?? [];
			}
		} finally {
			if (seq === requestSeq) {
				isFiltering = false;
			}
		}
	}

	async function selectCategory(cat: string) {
		selectedCategory = cat;
		await reloadFeed();
	}

	async function toggleTag(tag: string) {
		if (tag === 'All' || selectedTag === tag) {
			selectedTag = 'all';
		} else {
			selectedTag = tag;
		}
		await reloadFeed();
	}

	async function clearFilters() {
		if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
		selectedCategory = 'all';
		selectedTag = 'all';
		searchQuery = '';
		await reloadFeed();
	}

	function handleSearchInput(e: Event) {
		searchQuery = (e.currentTarget as HTMLInputElement).value;
		if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
		searchDebounceTimer = setTimeout(() => {
			void reloadFeed();
		}, 280);
	}

	async function handleRefresh() {
		isRefreshing = true;
		try {
			await reloadFeed({ refresh: true });
		} finally {
			isRefreshing = false;
		}
	}

	async function loadMore() {
		if (!hasMore || isLoadingMore || isFiltering) return;
		isLoadingMore = true;
		try {
			const res = await fetchArsenalNewsResult({
				limit: PAGE_SIZE,
				offset: articles.length,
				category: selectedCategory,
				tag: selectedTag,
				search: searchQuery
			});
			if (res.error) {
				apiError = res.error;
				return;
			}
			apiError = null;
			const seen = new Set(articles.map((a) => a.id));
			const incoming = (res.data.articles ?? []).filter((a) => !seen.has(a.id));
			articles = [...articles, ...incoming];
			total = res.data.total ?? articles.length;
			hasMore = Boolean(res.data.has_more) && incoming.length > 0;
			if (res.data.sources_active?.length) {
				sourcesActive = res.data.sources_active;
			}
		} finally {
			isLoadingMore = false;
		}
	}

	$effect(() => {
		if (!sentinelEl || !hasMore) return;
		if (typeof IntersectionObserver === 'undefined') return;

		const observer = new IntersectionObserver(
			(entries) => {
				if (entries.some((entry) => entry.isIntersecting)) {
					void loadMore();
				}
			},
			{ rootMargin: '240px 0px' }
		);

		observer.observe(sentinelEl);
		return () => {
			observer.disconnect();
		};
	});

	$effect(() => {
		return () => {
			if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
		};
	});

	function formatTimeAgo(isoOrDateStr: string): string {
		try {
			const d = new Date(isoOrDateStr);
			if (isNaN(d.getTime())) return isoOrDateStr;
			const diffMs = Date.now() - d.getTime();
			const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
			if (diffHrs < 1) return 'Just now';
			if (diffHrs < 24) return `${diffHrs}h ago`;
			const diffDays = Math.floor(diffHrs / 24);
			if (diffDays < 7) return `${diffDays}d ago`;
			return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
		} catch {
			return isoOrDateStr;
		}
	}
</script>

<svelte:head>
	<title>The Armory | Live Arsenal News Aggregator</title>
</svelte:head>

<div class="container py-12 space-y-10">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
		<div class="space-y-3">
			<h1 class="text-[length:var(--text-display-s)]">The Armory news wire</h1>
			<p class="lead text-ink-2">
				Aggregated coverage and tactical debriefs from Pain in the Arsenal, Arseblog, BBC Sport, and r/Gunners.
			</p>
		</div>

		<button
			type="button"
			onclick={handleRefresh}
			disabled={isRefreshing}
			class="inline-flex items-center gap-2 min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors self-start md:self-auto whitespace-nowrap"
		>
			<svg
				class="w-4 h-4 shrink-0 {isRefreshing ? 'motion-safe:animate-spin text-accent-text' : 'text-muted'}"
				aria-hidden="true"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
				/>
			</svg>
			<span>{refreshBtnText}</span>
		</button>
	</div>

	<!-- Controls & Category Tabs -->
	<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
		<!-- Category Filter Tabs -->
		<div class="flex items-center gap-2 flex-wrap">
			{#each categories as cat (cat.id)}
				{@const active = selectedCategory === cat.id}
				<button
					type="button"
					aria-pressed={active}
					onclick={() => selectCategory(cat.id)}
					class="min-h-[44px] px-3.5 rounded-card text-sm font-semibold transition-colors border whitespace-nowrap {active ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink hover:bg-paper-3'}"
				>
					{cat.label}
				</button>
			{/each}
		</div>

		<!-- Live Keyword Search -->
		<div class="relative w-full lg:w-80">
			<input
				type="search"
				aria-label="Filter headlines by keyword or player"
				value={searchQuery}
				oninput={handleSearchInput}
				placeholder="Filter headlines, Arteta, Saka…"
				class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card pl-9 pr-3 text-sm text-ink placeholder-muted transition-colors"
			/>
			<svg
				class="w-4 h-4 text-muted absolute left-3 top-3.5 shrink-0"
				aria-hidden="true"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
		</div>
	</div>

	<!-- Quick Topic & Player Tags Bar -->
	<div class="flex items-center gap-2 flex-wrap border-y border-rule py-3">
		<span class="text-xs text-muted mr-1">Filter by topic:</span>
		{#each quickTags as tag (tag)}
			{@const isActive = (tag === 'All' && selectedTag === 'all') || selectedTag === tag}
			<button
				type="button"
				aria-pressed={isActive}
				onclick={() => toggleTag(tag)}
				class="min-h-[44px] px-3 rounded-card text-xs font-semibold transition-colors border whitespace-nowrap {isActive ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper text-muted border-rule hover:text-ink'}"
			>
				#{tag}
			</button>
		{/each}
		{#if hasActiveFilters}
			<button
				type="button"
				onclick={clearFilters}
				class="min-h-[44px] px-3 rounded-card text-xs font-semibold text-accent-text hover:underline whitespace-nowrap"
			>
				Reset filters
			</button>
		{/if}
	</div>

	<!-- Active Sources Bar & Live Count -->
	<div class="flex items-center justify-between flex-wrap gap-3 text-xs text-muted">
		<div class="min-w-0">
			{#if sourcesActive.length > 0}
				<span>Active syndication sources: </span>
				<span class="text-ink-2 font-semibold">{sourcesActive.join(', ')}</span>
			{/if}
		</div>
		<div role="status" aria-live="polite" class="num flex items-center gap-2">
			{#if isFiltering}
				<span class="text-accent-2 font-semibold">Updating dispatches…</span>
			{/if}
			<span>Showing {articles.length} of {total} dispatches</span>
		</div>
	</div>

	{#if apiError}
		<StateBanner
			variant="error"
			title="The Armory wire is temporarily unavailable"
			message={apiError}
			busy={isFiltering || isRefreshing}
			onretry={() => reloadFeed({ refresh: true })}
		/>
	{/if}

	<!-- Articles Grid -->
	{#if isFiltering && articles.length === 0}
		<div role="status" class="border-t border-rule pt-10 text-sm text-muted">
			Filtering Arsenal dispatches…
		</div>
	{:else if articles.length === 0 && !apiError}
		<StateBanner
			variant="empty"
			title="No matching news dispatches"
			message="No dispatches matched your active category, topic tag, or search query."
			retryLabel={hasActiveFilters ? 'Reset filters' : 'Refresh feeds'}
			onretry={hasActiveFilters ? clearFilters : handleRefresh}
		/>
	{:else if articles.length > 0}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-8 {isFiltering ? 'opacity-70 transition-opacity' : ''}">
			{#each articles as art, idx (art.id)}
				<a
					href={art.article_url}
					target="_blank"
					rel="noopener noreferrer"
					class="group border-t border-rule pt-5 flex flex-col justify-between space-y-4 hover:border-rule-2 transition-colors"
				>
					<div class="space-y-3">
						<!-- Source Name & Timestamp Header -->
						<div class="flex items-center justify-between text-xs text-muted">
							<span class="font-semibold text-ink-2">{art.source_name}</span>
							<time class="num">{formatTimeAgo(art.published_at)}</time>
						</div>

						<!-- Image Thumbnail (collapses cleanly if image fails) -->
						{#if art.image_url && !failedImages[art.id]}
							<div class="w-full h-52 rounded-card overflow-hidden bg-paper-2 border border-rule">
								<img
									src={art.image_url}
									alt={art.title}
									width="640"
									height="360"
									loading={idx < 2 ? 'eager' : 'lazy'}
									fetchpriority={idx === 0 ? 'high' : 'auto'}
									class="w-full h-full object-cover"
									onerror={() => {
										failedImages = { ...failedImages, [art.id]: true };
									}}
								/>
							</div>
						{/if}

						<!-- Title -->
						<h3 class="text-base font-bold text-ink group-hover:text-accent-text transition-colors line-clamp-2 card-headline">
							{art.title}
						</h3>

						<!-- Summary / Snippet -->
						<p class="text-sm text-ink-2 line-clamp-3">
							{art.summary}
						</p>

						<!-- Dynamic Entity Tags -->
						{#if art.tags && art.tags.length > 0}
							<div class="flex items-center gap-2 flex-wrap pt-1 text-xs text-muted">
								{#each art.tags as tag, tIdx (tIdx)}
									<span>#{tag}</span>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Outbound Redirect Footer -->
					<div class="pt-3 border-t border-rule flex items-center justify-between text-xs text-muted">
						<span>Source: {art.source_name}</span>
						<span class="font-semibold text-accent-text group-hover:underline">
							Read dispatch<span class="visually-hidden"> (opens in a new tab)</span>
						</span>
					</div>
				</a>
			{/each}
		</div>

		<!-- Infinite Scroll Sentinel & Accessible Load More Fallback -->
		{#if hasMore}
			<div bind:this={sentinelEl} class="pt-6 border-t border-rule flex flex-col items-center gap-3">
				<button
					type="button"
					onclick={loadMore}
					disabled={isLoadingMore}
					class="inline-flex items-center min-h-[44px] px-5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors whitespace-nowrap"
				>
					{loadMoreLabel}
				</button>
			</div>
		{/if}
	{/if}
</div>
