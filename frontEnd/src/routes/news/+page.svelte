<script lang="ts">
	import { fetchArsenalNews } from '$lib/api/football';
	import type { NewsFeed, NewsItem } from '$lib/types/football';
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

	$effect(() => {
		feed = data.feed;
		selectedCategory = data.category || 'all';
	});

	const categories = [
		{ id: 'all', label: 'All Updates' },
		{ id: 'fan_blog', label: 'Fan Blogs (Pain in the Arsenal, Arseblog)' },
		{ id: 'reddit', label: 'r/Gunners Top Week' },
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

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6">
	<!-- Page Header -->
	<div class="border-b border-[#1e2430] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-red-950/70 text-red-400 border border-red-800/40 font-mono">
				Live Multi-Source Aggregator
			</div>
			<h1 class="text-3xl font-black text-white uppercase tracking-tight flex items-center gap-2">
				<span>The Armory News</span>
			</h1>
			<p class="text-sm text-gray-400 mt-1 max-w-2xl">
				Aggregated match coverage, tactical debriefs, and community discussions directly from
				<strong class="text-white">Pain in the Arsenal</strong>,
				<strong class="text-white">Arseblog News</strong>,
				<strong class="text-white">BBC Sport</strong>, and
				<strong class="text-white">Reddit r/Gunners</strong>.
			</p>
		</div>

		<button
			type="button"
			onclick={handleRefresh}
			disabled={isRefreshing}
			class="px-4 py-2 rounded-lg bg-[#12161f] border border-[#1e2430] hover:border-gray-500 text-xs font-semibold text-gray-300 hover:text-white transition flex items-center gap-2 self-start md:self-auto disabled:opacity-50"
		>
			<svg
				class="w-3.5 h-3.5 {isRefreshing ? 'animate-spin text-red-500' : 'text-gray-400'}"
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
			<span>{isRefreshing ? 'Syncing Feeds...' : 'Refresh Feeds'}</span>
		</button>
	</div>

	<!-- Controls & Category Tabs -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<!-- Category Filter Tabs -->
		<div class="flex items-center gap-1.5 flex-wrap">
			{#each categories as cat}
				<button
					type="button"
					onclick={() => selectCategory(cat.id)}
					class="px-3 py-1.5 rounded-lg text-xs font-semibold transition border {selectedCategory === cat.id ? 'bg-red-600 text-white border-red-500' : 'bg-[#12161f] text-gray-400 border-[#1e2430] hover:text-white'}"
				>
					{cat.label}
				</button>
			{/each}
		</div>

		<!-- Live Keyword Search -->
		<div class="relative w-full sm:w-72">
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Filter headlines, Arteta, Saka..."
				class="w-full bg-[#12161f] border border-[#1e2430] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition"
			/>
			<svg
				class="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
		</div>
	</div>

	<!-- Quick Topic & Player Tags Bar -->
	<div class="flex items-center gap-1.5 flex-wrap">
		<span class="text-[11px] text-gray-500 uppercase font-mono mr-1">Smart Tags:</span>
		{#each quickTags as tag}
			{@const isActive = (tag === 'All' && selectedTag === 'all') || selectedTag === tag}
			<button
				type="button"
				onclick={() => toggleTag(tag)}
				class="px-2.5 py-1 rounded-full text-[11px] font-mono transition border {isActive ? 'bg-amber-400 text-black font-bold border-amber-300' : 'bg-[#12161f] text-gray-400 border-[#1e2430] hover:text-white hover:border-gray-600'}"
			>
				#{tag}
			</button>
		{/each}
	</div>

	<!-- Active Sources Bar -->
	{#if feed && feed.sources_active}
		<div class="p-3 rounded-lg border border-[#1e2430] bg-[#0d1017] flex items-center justify-between flex-wrap gap-2 text-[11px] text-gray-400 font-mono">
			<div class="flex items-center gap-2">
				<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
				<span class="text-gray-500 uppercase">Active Ingestion:</span>
				<span class="text-gray-300">{feed.sources_active.join(' • ')}</span>
			</div>
			<div class="text-gray-500">
				Showing {filteredArticles.length} articles (Shuffled & Normalized)
			</div>
		</div>
	{/if}

	<!-- Articles Grid -->
	{#if filteredArticles.length === 0}
		<div class="p-12 text-center rounded-xl border border-[#1e2430] bg-[#12161f] text-gray-500 space-y-2">
			<p class="text-sm font-semibold text-gray-300">No news articles found</p>
			<p class="text-xs">Try clearing your search query or refreshing the news streams.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
			{#each filteredArticles as art}
				<a
					href={art.article_url}
					target="_blank"
					rel="noopener noreferrer"
					class="group block p-4 rounded-xl border border-[#1e2430] bg-[#12161f] hover:border-red-600/50 hover:bg-[#161b26] transition flex flex-col justify-between space-y-3.5 shadow-sm"
				>
					<div class="space-y-3">
						<!-- Source Badge & Timestamp Header -->
						<div class="flex items-center justify-between text-[11px]">
							<span
								class="px-2 py-0.5 rounded font-mono font-bold flex items-center gap-1.5"
								style="background-color: {art.source_color}20; color: {art.source_color}; border: 1px solid {art.source_color}40;"
							>
								<span class="w-1.5 h-1.5 rounded-full" style="background-color: {art.source_color}"></span>
								<span>{art.source_name}</span>
							</span>
							<span class="text-gray-500 font-mono">{formatTimeAgo(art.published_at)}</span>
						</div>

						<!-- Image Thumbnail (if present) -->
						{#if art.image_url}
							<div class="w-full h-36 rounded-lg overflow-hidden bg-black/40 border border-[#1e2430]">
								<img
									src={art.image_url}
									alt={art.title}
									loading="lazy"
									class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
									onerror={(e) => ((e.currentTarget as HTMLElement).style.display = 'none')}
								/>
							</div>
						{/if}

						<!-- Title -->
						<h3 class="text-sm font-bold text-white group-hover:text-red-400 transition leading-snug line-clamp-2">
							{art.title}
						</h3>

						<!-- Summary / Snippet -->
						<p class="text-xs text-gray-400 line-clamp-3 leading-relaxed">
							{art.summary}
						</p>

						<!-- Dynamic Entity Tags -->
						{#if art.tags && art.tags.length > 0}
							<div class="flex items-center gap-1.5 flex-wrap pt-1">
								{#each art.tags as tag}
									<span
										class="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-gray-300 group-hover:border-amber-400/40 group-hover:text-amber-300 transition"
									>
										#{tag}
									</span>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Outbound Redirect Footer -->
					<div class="pt-3 border-t border-[#1e2430] flex items-center justify-between text-xs text-gray-500">
						<span class="text-[10px] font-mono text-gray-400">Read on {art.source_name}</span>
						<span class="text-red-400 group-hover:translate-x-0.5 transition font-bold font-mono">
							Open ↗
						</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
