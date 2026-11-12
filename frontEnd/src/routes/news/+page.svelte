<script lang="ts">
	import { fetchArsenalNews } from '$lib/api/football';
	import type { NewsFeed } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let feed = $state<NewsFeed>({
		articles: [],
		total: 0,
		sources_active: [],
		cached_at: ''
	});
	let selectedCategory = $state<string>('all');
	let selectedTag = $state<string>('all');
	let searchQuery = $state<string>('');
	let isRefreshing = $state<boolean>(false);
	let refreshBtnText = $derived(isRefreshing ? 'Syncing…' : 'Sync feeds');

	$effect(() => {
		feed = data.feed;
		selectedCategory = data.category || 'all';
	});

	const categories = [
		{ id: 'all', label: 'All updates' },
		{ id: 'fan_blog', label: 'Fan blogs (Pain in the Arsenal, Arseblog)' },
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

	async function selectCategory(cat: string) {
		selectedCategory = cat;
		feed = await fetchArsenalNews(cat);
	}

	function toggleTag(tag: string) {
		if (tag === 'All' || selectedTag === tag) {
			selectedTag = 'all';
		} else {
			selectedTag = tag;
		}
	}

	async function handleRefresh() {
		isRefreshing = true;
		try {
			feed = await fetchArsenalNews(selectedCategory, true);
		} finally {
			isRefreshing = false;
		}
	}

	const filteredArticles = $derived.by(() => {
		if (!feed || !feed.articles) return [];
		let list = feed.articles;

		if (selectedTag !== 'all') {
			const tagLower = selectedTag.toLowerCase();
			list = list.filter((a) => {
				const hasTag = a.tags && a.tags.some((t) => t.toLowerCase() === tagLower);
				const inTitle = a.title.toLowerCase().includes(tagLower);
				return hasTag || inTitle;
			});
		}

		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(a) =>
					a.title.toLowerCase().includes(q) ||
					a.summary.toLowerCase().includes(q) ||
					(a.tags && a.tags.some((t) => t.toLowerCase().includes(q)))
			);
		}
		return list;
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
			<h1>The Armory news wire</h1>
			<p class="lead text-ink-2">
				Aggregated coverage and tactical debriefs from Pain in the Arsenal, Arseblog, BBC Sport, and r/Gunners.
			</p>
		</div>

		<button
			type="button"
			onclick={handleRefresh}
			disabled={isRefreshing}
			class="inline-flex items-center gap-2 h-10 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors self-start md:self-auto whitespace-nowrap"
		>
			<svg
				class="w-4 h-4 shrink-0 {isRefreshing ? 'motion-safe:animate-spin text-accent' : 'text-muted'}"
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
			{#each categories as cat}
				<button
					type="button"
					onclick={() => selectCategory(cat.id)}
					class="h-9 px-3.5 rounded-card text-sm font-semibold transition-colors border whitespace-nowrap {selectedCategory === cat.id ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink hover:bg-paper-3'}"
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
				bind:value={searchQuery}
				placeholder="Filter headlines, Arteta, Saka…"
				class="w-full h-10 bg-paper-2 border border-rule rounded-card pl-9 pr-3 text-sm text-ink placeholder-muted transition-colors"
			/>
			<svg
				class="w-4 h-4 text-muted absolute left-3 top-3 shrink-0"
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
		{#each quickTags as tag}
			{@const isActive = (tag === 'All' && selectedTag === 'all') || selectedTag === tag}
			<button
				type="button"
				onclick={() => toggleTag(tag)}
				class="h-7 px-2.5 rounded-card text-xs font-semibold transition-colors border whitespace-nowrap {isActive ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper text-muted border-rule hover:text-ink'}"
			>
				#{tag}
			</button>
		{/each}
	</div>

	<!-- Active Sources Bar -->
	{#if feed && feed.sources_active}
		<div class="flex items-center justify-between flex-wrap gap-3 text-xs text-muted">
			<div>
				<span>Active syndication sources: </span>
				<span class="text-ink-2 font-semibold">{feed.sources_active.join(', ')}</span>
			</div>
			<div class="num">
				Showing {filteredArticles.length} dispatches
			</div>
		</div>
	{/if}

	<!-- Articles Grid -->
	{#if filteredArticles.length === 0}
		<div class="border-t border-rule pt-10 space-y-2">
			<h2 class="text-lg font-semibold text-ink">No matching news dispatches</h2>
			<p class="text-sm text-muted">Clear your search filter or refresh the live syndication feeds.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
			{#each filteredArticles as art, idx}
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

						<!-- Image Thumbnail (if present) -->
						{#if art.image_url}
							<div class="w-full h-44 rounded-card overflow-hidden bg-paper-2 border border-rule">
								<img
									src={art.image_url}
									alt={art.title}
									width="400"
									height="225"
									loading={idx === 0 ? 'eager' : 'lazy'}
									fetchpriority={idx === 0 ? 'high' : 'auto'}
									class="w-full h-full object-cover"
									onerror={(e) => ((e.currentTarget as HTMLElement).style.display = 'none')}
								/>
							</div>
						{/if}

						<!-- Title -->
						<h3 class="text-base font-bold text-ink group-hover:text-accent transition-colors line-clamp-2">
							{art.title}
						</h3>

						<!-- Summary / Snippet -->
						<p class="text-sm text-ink-2 line-clamp-3">
							{art.summary}
						</p>

						<!-- Dynamic Entity Tags -->
						{#if art.tags && art.tags.length > 0}
							<div class="flex items-center gap-2 flex-wrap pt-1 text-xs text-muted">
								{#each art.tags as tag}
									<span>#{tag}</span>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Outbound Redirect Footer -->
					<div class="pt-3 border-t border-rule flex items-center justify-between text-xs text-muted">
						<span>Source: {art.source_name}</span>
						<span class="font-semibold text-accent group-hover:underline">Read dispatch</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
