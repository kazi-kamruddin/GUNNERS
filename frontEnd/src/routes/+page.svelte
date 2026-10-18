<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { fetchMatchSummary } from '$lib/api/football';
	import type { MatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let summary = $state<MatchSummary | null>(null);
	let isLoadingSummary = $state(false);
	let isInitialized = false;

	const clubList = Object.values(CLUBS);
	const viewingClub = $derived(themeState.currentTheme);

	$effect(() => {
		if (!isInitialized && data.summary) {
			summary = data.summary;
			isInitialized = true;
		}
	});

	$effect(() => {
		const clubId = themeState.viewingClubId;
		if (isInitialized && clubId) {
			loadSummaryForClub(clubId);
		}
	});

	async function loadSummaryForClub(clubId: string) {
		isLoadingSummary = true;
		try {
			const res = await fetchMatchSummary(clubId);
			if (res) summary = res;
		} finally {
			isLoadingSummary = false;
		}
	}

	function formatDate(utcString?: string): string {
		if (!utcString) return 'TBD';
		try {
			const d = new Date(utcString);
			return d.toLocaleDateString(undefined, {
				month: 'short',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return utcString;
		}
	}
</script>

<svelte:head>
	<title>{viewingClub.name} | GUNNERS Reborn Fan Portal</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-10">
	<!-- Hero Section -->
	<section class="relative rounded-2xl p-6 sm:p-10 overflow-hidden border border-[#1e2430] bg-gradient-to-br from-[#12161f] via-[#151a24] to-[#0d1017]">
		<div
			class="absolute -right-20 -bottom-20 w-96 h-96 rounded-full blur-3xl opacity-20 pointer-events-none transition-all duration-700"
			style="background-color: {viewingClub.primary_color}"
		></div>

		<div class="relative z-10 max-w-3xl">
			<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-4 bg-white/5 border border-white/10 text-gray-300">
				<span class="w-2 h-2 rounded-full" style="background-color: {viewingClub.primary_color}"></span>
				<span>{viewingClub.name} • {viewingClub.league}</span>
			</div>

			<h1 class="text-3xl sm:text-5xl font-black tracking-tight text-white mb-4">
				Football Analytics.<br />
				<span class="bg-gradient-to-r from-red-500 via-amber-400 to-amber-200 bg-clip-text text-transparent">
					Anchored in Evidence.
				</span>
			</h1>

			<p class="text-sm sm:text-base text-gray-400 mb-6 leading-relaxed max-w-2xl">
				Explore verified metrics, create shareable visual insights in the Data Lab, and debate rivals on The Terrace with real match data.
			</p>

			<div class="flex flex-wrap items-center gap-3">
				<a
					href="/lab"
					class="px-5 py-2.5 rounded-lg bg-red-600 hover:bg-red-500 font-bold text-xs sm:text-sm text-white transition shadow-md flex items-center gap-2"
				>
					<span>Launch Data Lab</span>
					<span>→</span>
				</a>
				<a
					href="/terrace"
					class="px-5 py-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs sm:text-sm font-semibold text-gray-200 transition"
				>
					The Terrace Feed
				</a>
				<a
					href="/messages"
					class="px-5 py-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs sm:text-sm font-semibold text-amber-400 transition"
				>
					💬 Dressing Room
				</a>
			</div>
		</div>
	</section>

	<!-- Club Universe Switcher Bar -->
	<section>
		<div class="flex items-center justify-between mb-4">
			<div>
				<h2 class="text-lg font-bold text-white uppercase tracking-tight">Club Universe</h2>
				<p class="text-xs text-gray-400">Switch active viewing club to personalize analytics and schedules</p>
			</div>
			<span class="text-[11px] font-mono text-gray-500">4 Foundation Clubs</span>
		</div>

		<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
			{#each clubList as club}
				{@const isSelected = viewingClub.id === club.id}
				<button
					type="button"
					onclick={() => themeState.setViewingClub(club.id)}
					class="p-4 rounded-xl border text-left transition-all duration-200 relative group overflow-hidden {isSelected ? 'border-white/40 bg-[#161c28]' : 'border-[#1e2430] bg-[#12161f]/60 hover:border-gray-700'}"
				>
					<div class="flex items-center gap-2 mb-2">
						<span class="w-3 h-3 rounded-full" style="background-color: {club.primary_color}"></span>
						<span class="text-xs font-bold text-white">{club.short_name}</span>
					</div>
					<p class="text-[11px] text-gray-400 truncate">{club.league}</p>
					{#if isSelected}
						<div class="mt-2 text-[10px] font-mono font-bold text-amber-400">
							● Viewing
						</div>
					{/if}
				</button>
			{/each}
		</div>
	</section>

	<!-- Match Hub & Recent Form Card -->
	<section class="grid grid-cols-1 md:grid-cols-3 gap-6">
		<!-- Next Fixture -->
		<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
			<div>
				<div class="flex items-center justify-between mb-3">
					<span class="text-[10px] font-bold font-mono uppercase tracking-wider text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
						Next Fixture
					</span>
					<a href="/matches" class="text-[11px] text-gray-400 hover:text-white transition">View All →</a>
				</div>

				{#if summary?.next_fixture}
					<div class="space-y-3 mt-4">
						<div class="text-xs font-mono text-gray-400">
							{summary.next_fixture.competition_name || 'Matchday'} • {formatDate(summary.next_fixture.utc_date)}
						</div>
						<div class="flex items-center justify-between gap-3 bg-[#0d1017] p-3 rounded-lg border border-[#1e2430]">
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.next_fixture.home_team_name}</p>
								<p class="text-[10px] text-gray-500">Home</p>
							</div>
							<span class="text-xs font-bold text-gray-500">VS</span>
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.next_fixture.away_team_name}</p>
								<p class="text-[10px] text-gray-500">Away</p>
							</div>
						</div>
						<p class="text-[11px] text-gray-400 text-center font-mono">
							📍 {summary.next_fixture.venue || 'Stadium'}
						</p>
					</div>
				{:else}
					<div class="py-8 text-center text-gray-500 text-xs">
						No upcoming matches scheduled.
					</div>
				{/if}
			</div>

			<div class="mt-4 pt-3 border-t border-[#1e2430] flex items-center justify-between text-[11px] text-gray-400">
				<span>Completed: {summary?.total_completed ?? 0}</span>
				<span>Scheduled: {summary?.total_scheduled ?? 0}</span>
			</div>
		</div>

		<!-- Last Result -->
		<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
			<div>
				<div class="flex items-center justify-between mb-3">
					<span class="text-[10px] font-bold font-mono uppercase tracking-wider text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">
						Latest Result
					</span>
					<span class="text-[11px] font-mono text-gray-500">{summary?.last_result ? formatDate(summary.last_result.utc_date) : ''}</span>
				</div>

				{#if summary?.last_result}
					<div class="space-y-3 mt-4">
						<div class="flex items-center justify-between gap-3 bg-[#0d1017] p-3 rounded-lg border border-[#1e2430]">
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.last_result.home_team_name}</p>
								<span class="text-xl font-black text-white">{summary.last_result.home_score ?? 0}</span>
							</div>
							<span class="text-xs font-bold text-gray-600">-</span>
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.last_result.away_team_name}</p>
								<span class="text-xl font-black text-white">{summary.last_result.away_score ?? 0}</span>
							</div>
						</div>
						<p class="text-[11px] text-gray-400 text-center font-mono">
							{summary.last_result.competition_name || 'League Match'}
						</p>
					</div>
				{:else}
					<div class="py-8 text-center text-gray-500 text-xs">
						No completed results found.
					</div>
				{/if}
			</div>

			<!-- Recent Form Guide -->
			<div class="mt-4 pt-3 border-t border-[#1e2430] flex items-center justify-between">
				<span class="text-[11px] text-gray-400">Form (Last 5):</span>
				<div class="flex items-center gap-1.5">
					{#if summary?.recent_form && summary.recent_form.length > 0}
						{#each summary.recent_form as item}
							<span
								class="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold font-mono {item === 'W' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : item === 'D' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' : 'bg-red-500/20 text-red-400 border border-red-500/40'}"
							>
								{item}
							</span>
						{/each}
					{:else}
						<span class="text-xs text-gray-500 font-mono">-</span>
					{/if}
				</div>
			</div>
		</div>

		<!-- Fast Analytics Query Teaser -->
		<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
			<div>
				<div class="flex items-center justify-between mb-3">
					<span class="text-[10px] font-bold font-mono uppercase tracking-wider text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded border border-purple-400/20">
						Data Lab Quick Launch
					</span>
				</div>
				<h3 class="text-sm font-bold text-white mb-2">Explore Club Form & Metrics</h3>
				<p class="text-xs text-gray-400 leading-relaxed">
					Analyze Win Rates, Goals Per Match, Clean Sheets, and Points Per Game with home/away venue isolation.
				</p>
				<div class="mt-4 flex flex-wrap gap-1.5">
					<a
						href="/lab?metric=win_rate&teams={viewingClub.id}&venue=all"
						class="text-[10px] px-2 py-1 rounded bg-[#0d1017] border border-[#1e2430] text-gray-300 hover:text-white hover:border-gray-500 transition"
					>
						Win Rate (%)
					</a>
					<a
						href="/lab?metric=goals_per_match&teams={viewingClub.id}&venue=all"
						class="text-[10px] px-2 py-1 rounded bg-[#0d1017] border border-[#1e2430] text-gray-300 hover:text-white hover:border-gray-500 transition"
					>
						Goals / Match
					</a>
					<a
						href="/lab?metric=points_per_game&teams={viewingClub.id}&venue=all"
						class="text-[10px] px-2 py-1 rounded bg-[#0d1017] border border-[#1e2430] text-gray-300 hover:text-white hover:border-gray-500 transition"
					>
						PPG
					</a>
				</div>
			</div>

			<a
				href="/lab?teams={viewingClub.id}"
				class="mt-6 w-full py-2 text-center rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs font-bold text-white transition"
			>
				Open Full Analytics Engine →
			</a>
		</div>
	</section>

	<!-- Featured Insights Shelf -->
	<section class="space-y-4">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="text-lg font-bold text-white uppercase tracking-tight">Community Evidence Shelf</h2>
				<p class="text-xs text-gray-400">Peer-reviewed tactical insights published directly from the Data Lab</p>
			</div>
			<a href="/lab" class="text-xs text-amber-400 hover:text-amber-300 font-semibold transition">
				Create Insight →
			</a>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			{#if data.insights && data.insights.length > 0}
				{#each data.insights as ins}
					{@const authorClub = CLUBS[ins.author_club_id] || CLUBS['arsenal']}
					<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between space-y-3">
						<div>
							<div class="flex items-center justify-between mb-2">
								<div class="flex items-center gap-1.5">
									<span class="w-2 h-2 rounded-full" style="background-color: {authorClub.primary_color}"></span>
									<span class="text-[11px] font-bold text-gray-300">{ins.author_name}</span>
								</div>
								<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-amber-400 border border-[#1e2430]">
									{ins.metric.replace('_', ' ').toUpperCase()}
								</span>
							</div>

							<h4 class="text-xs font-bold text-white mb-1">{ins.title}</h4>
							{#if ins.description}
								<p class="text-[11px] text-gray-400 line-clamp-2">{ins.description}</p>
							{/if}
						</div>

						<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between">
							<span class="text-[10px] text-gray-500 font-mono">
								{ins.snapshot?.series?.length || 0} teams evaluated
							</span>
							<a
								href="/lab?metric={ins.metric}&teams={ins.team_ids.join(',')}&venue={ins.venue}"
								class="text-[11px] text-amber-400 hover:text-amber-300 font-bold transition flex items-center gap-1"
							>
								<span>Examine</span>
								<span>→</span>
							</a>
						</div>
					</div>
				{/each}
			{:else}
				<div class="col-span-3 py-8 text-center text-gray-500 text-xs border border-dashed border-[#1e2430] rounded-xl">
					No community insights published yet.
				</div>
			{/if}
		</div>
	</section>

	<!-- The Terrace Pulse -->
	<section class="space-y-4">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="text-lg font-bold text-white uppercase tracking-tight">The Terrace Pulse</h2>
				<p class="text-xs text-gray-400">Latest active debates and supporter opinions</p>
			</div>
			<a href="/terrace" class="text-xs text-red-400 hover:text-red-300 font-semibold transition">
				Visit Terrace →
			</a>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			{#if data.posts && data.posts.length > 0}
				{#each data.posts as post}
					{@const authorClub = CLUBS[post.author_club_id] || CLUBS['arsenal']}
					<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-2.5">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-2">
								<span class="w-2.5 h-2.5 rounded-full" style="background-color: {authorClub.primary_color}"></span>
								<span class="text-xs font-bold text-white">{post.author_name}</span>
								<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-gray-400 border border-[#1e2430]">
									{authorClub.short_name}
								</span>
							</div>
							<a
								href="/messages?recipient={encodeURIComponent(post.author_id || post.author_name)}&name={encodeURIComponent(post.author_name)}&club={encodeURIComponent(post.author_club_id)}"
								class="text-[10px] text-gray-400 hover:text-amber-400 font-semibold transition flex items-center gap-0.5"
								title="Direct message {post.author_name}"
							>
								<span>💬</span>
								<span>DM</span>
							</a>
						</div>

						<p class="text-xs text-gray-300 line-clamp-2 leading-relaxed">
							{post.content}
						</p>

						<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-[10px] text-gray-500 font-mono">
							<span>🔥 {post.reactions_count} cheers • 💬 {post.comments_count} replies</span>
							<a href="/terrace" class="text-gray-400 hover:text-white transition">Join Debate →</a>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</section>

	<!-- Footer Pipeline Sync Badge -->
	<section class="p-4 rounded-xl border border-[#1e2430] bg-[#0d1017] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-gray-500">
		<div class="flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
			<span class="font-bold text-gray-400">Data Pipeline:</span>
			<span>{data.syncStatus?.source || 'football-data.org (Active)'}</span>
		</div>
		<div class="flex items-center gap-4 text-[11px] font-mono">
			<span>Synced: {data.syncStatus?.matches_synced ?? 0} matches</span>
			<span>Status: <strong class="text-emerald-400">{data.syncStatus?.status || 'HEALTHY'}</strong></span>
		</div>
	</section>
</div>
