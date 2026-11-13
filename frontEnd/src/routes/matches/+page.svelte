<script lang="ts">
	import { replaceState } from '$app/navigation';
	import { page } from '$app/state';
	import { untrack } from 'svelte';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { fetchMatchesResult } from '$lib/api/football';
	import { formatMatchDateTime } from '$lib/utils/format';
	import type { Match, MatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	function normalizeStatus(val: string | undefined): 'ALL' | 'SCHEDULED' | 'FINISHED' {
		if (val === 'SCHEDULED' || val === 'FINISHED') return val;
		return 'ALL';
	}

	let activeTab = $state<'ALL' | 'SCHEDULED' | 'FINISHED'>(untrack(() => normalizeStatus(data.activeStatus)));
	let selectedComp = $state<string>(untrack(() => data.activeComp || 'ALL'));
	let selectedSeason = $state<string>(untrack(() => data.activeSeasonId || 'all'));
	let isLoading = $state(false);

	let matches = $state<Match[]>(untrack(() => data.initialMatches ?? []));
	let matchesError = $state<string | null>(untrack(() => data.matchesError ?? null));
	let summary = $state<MatchSummary | null>(untrack(() => data.initialSummary ?? null));
	let failedCrests = $state<Record<string, boolean>>({});
	let requestSeq = 0;

	let syncStatus = $derived(data.syncStatus);
	let seasons = $derived(data.seasons || []);
	let currentSeasonDetail = $derived(
		selectedSeason !== 'all' ? seasons.find((s) => s.id === selectedSeason) : null
	);
	let previousResults = $derived(
		matches
			.filter((m) => m.status === 'FINISHED')
			.slice()
			.sort((a, b) => new Date(b.utc_date).getTime() - new Date(a.utc_date).getTime())
	);
	let upcomingFixtures = $derived(
		matches
			.filter((m) => m.status !== 'FINISHED')
			.slice()
			.sort((a, b) => new Date(a.utc_date).getTime() - new Date(b.utc_date).getTime())
	);

	$effect(() => {
		matches = data.initialMatches ?? [];
		matchesError = data.matchesError ?? null;
		summary = data.initialSummary ?? null;
		selectedSeason = data.activeSeasonId || 'all';
		selectedComp = data.activeComp || 'ALL';
		activeTab = normalizeStatus(data.activeStatus);
		failedCrests = {};
	});

	function syncMatchesUrl() {
		if (typeof window === 'undefined') return;
		const nextUrl = new URL(page.url.href);
		if (selectedComp !== 'ALL') nextUrl.searchParams.set('comp', selectedComp);
		else nextUrl.searchParams.delete('comp');
		if (activeTab !== 'ALL') nextUrl.searchParams.set('status', activeTab);
		else nextUrl.searchParams.delete('status');
		if (selectedSeason !== 'all') nextUrl.searchParams.set('season', selectedSeason);
		else nextUrl.searchParams.delete('season');
		replaceState(nextUrl, {});
	}

	async function applyFilters() {
		const seq = ++requestSeq;
		isLoading = true;
		syncMatchesUrl();
		try {
			const res = await fetchMatchesResult({
				club_id: 'arsenal',
				competition_id: selectedComp !== 'ALL' ? selectedComp : undefined,
				status: activeTab !== 'ALL' ? activeTab : undefined,
				season_id: selectedSeason !== 'all' ? selectedSeason : undefined,
				limit: 100
			});
			if (seq !== requestSeq) return;
			matchesError = res.error;
			if (!res.error) {
				matches = res.data;
			}
		} finally {
			if (seq === requestSeq) {
				isLoading = false;
			}
		}
	}

	async function resetFilters() {
		activeTab = 'ALL';
		selectedComp = 'ALL';
		selectedSeason = 'all';
		await applyFilters();
	}
</script>

<svelte:head>
	<title>Arsenal Match Schedule & Results | GUNNERS</title>
</svelte:head>

<div class="container py-8 space-y-8">
	<!-- Compact Quick Actions -->
	<div class="flex flex-wrap items-center justify-between gap-3 border-b border-rule pb-4">
		<div class="flex items-center gap-2 text-xs text-muted">
			<span class="font-semibold text-ink-2">Arsenal FC Schedule &amp; Results</span>
			{#if syncStatus}
				<span>·</span>
				<span class="num">{syncStatus.matches_synced} synced</span>
			{/if}
		</div>
		<div class="flex flex-wrap items-center gap-3">
			<a
				href="/predictions"
				class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 font-semibold text-sm transition-opacity whitespace-nowrap"
			>
				Match predictor
			</a>
			<a
				href="/board"
				class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 font-semibold text-sm text-ink transition-colors whitespace-nowrap"
			>
				Lineup studio
			</a>
		</div>
	</div>

	<!-- Form & Overview Well -->
	{#if summary}
		<div class="grid grid-cols-1 md:grid-cols-12 gap-8 bg-paper-2 border-t-2 border-rule-2 p-6">
			<!-- Recent Form -->
			<div class="md:col-span-4 space-y-3">
				<h2 class="text-base font-semibold text-ink card-headline">Recent form (last 5)</h2>
				<div class="flex items-center gap-2">
					{#if summary.recent_form.length > 0}
						{#each summary.recent_form as res, idx (idx)}
							<span
								class="num w-7 h-7 rounded-card inline-flex items-center justify-center font-semibold text-xs border border-rule bg-paper-3 {res === 'W' ? 'text-success' : res === 'D' ? 'text-accent-2' : 'text-error'}"
							>
								{res}
							</span>
						{/each}
					{:else}
						<span class="text-sm text-muted">No recent completed matches</span>
					{/if}
				</div>
				<div class="text-xs text-muted flex gap-4 num pt-1">
					<span>Completed: <strong class="text-ink font-semibold">{summary.total_completed}</strong></span>
					<span>Scheduled: <strong class="text-ink font-semibold">{summary.total_scheduled}</strong></span>
				</div>
			</div>

			<!-- Next Fixture Quick View -->
			<div class="md:col-span-8 md:border-l md:border-rule md:pl-8 space-y-3 min-w-0">
				<h2 class="text-base font-semibold text-ink card-headline">Next scheduled fixture</h2>
				{#if summary.next_fixture}
					{@const nextFixture = summary.next_fixture}
					<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
						<a href="/matches/{encodeURIComponent(nextFixture.id)}" class="flex flex-wrap items-center gap-3 group min-w-0">
							<div class="flex items-center gap-2 min-w-0">
								{#if nextFixture.home_team_crest && !failedCrests[`next-home-${nextFixture.id}`]}
									<img
										src={nextFixture.home_team_crest}
										alt=""
										width="24"
										height="24"
										class="w-6 h-6 object-contain shrink-0"
										onerror={() => (failedCrests = { ...failedCrests, [`next-home-${nextFixture.id}`]: true })}
									/>
								{/if}
								<span class="text-base font-bold text-ink group-hover:text-accent-text transition-colors truncate">{nextFixture.home_team_name}</span>
							</div>
							<span class="text-xs text-muted px-2 py-0.5 bg-paper-3 rounded-card shrink-0">vs</span>
							<div class="flex items-center gap-2 min-w-0">
								{#if nextFixture.away_team_crest && !failedCrests[`next-away-${nextFixture.id}`]}
									<img
										src={nextFixture.away_team_crest}
										alt=""
										width="24"
										height="24"
										class="w-6 h-6 object-contain shrink-0"
										onerror={() => (failedCrests = { ...failedCrests, [`next-away-${nextFixture.id}`]: true })}
									/>
								{/if}
								<span class="text-base font-bold text-ink group-hover:text-accent-text transition-colors truncate">{nextFixture.away_team_name}</span>
							</div>
						</a>
						<div class="sm:text-right shrink-0">
							<div class="num text-sm font-semibold text-accent-2">{formatMatchDateTime(nextFixture.utc_date)}</div>
							<div class="text-xs text-muted">{nextFixture.venue || nextFixture.competition_name}</div>
						</div>
					</div>
				{:else}
					<p class="text-sm text-muted">No upcoming fixtures scheduled in active window.</p>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Filter Controls -->
	<div class="flex flex-col xl:flex-row xl:items-center justify-between gap-4 border-b border-rule pb-5">
		<!-- Tab Switcher -->
		<div class="flex items-center gap-2 flex-wrap">
			<button
				type="button"
				aria-pressed={activeTab === 'ALL'}
				onclick={() => { activeTab = 'ALL'; applyFilters(); }}
				class="min-h-[44px] px-3.5 rounded-card transition-colors text-sm font-semibold border whitespace-nowrap {activeTab === 'ALL' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				All matches
			</button>
			<button
				type="button"
				aria-pressed={activeTab === 'SCHEDULED'}
				onclick={() => { activeTab = 'SCHEDULED'; applyFilters(); }}
				class="min-h-[44px] px-3.5 rounded-card transition-colors text-sm font-semibold border whitespace-nowrap {activeTab === 'SCHEDULED' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Upcoming fixtures
			</button>
			<button
				type="button"
				aria-pressed={activeTab === 'FINISHED'}
				onclick={() => { activeTab = 'FINISHED'; applyFilters(); }}
				class="min-h-[44px] px-3.5 rounded-card transition-colors text-sm font-semibold border whitespace-nowrap {activeTab === 'FINISHED' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Completed results
			</button>
		</div>

		<!-- Competition & Season Dropdowns -->
		<div class="flex flex-col sm:flex-row sm:items-center gap-3 text-sm w-full xl:w-auto min-w-0">
			<div class="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2 min-w-0">
				<label for="comp-select" class="text-muted text-xs shrink-0">Competition:</label>
				<select
					id="comp-select"
					bind:value={selectedComp}
					onchange={applyFilters}
					class="w-full sm:w-auto min-w-0 max-w-full min-h-[44px] bg-paper-2 border border-rule text-ink rounded-card px-3 text-sm"
				>
					<option value="ALL">All competitions</option>
					<option value="PL">Premier League</option>
					<option value="CL">Champions League</option>
				</select>
			</div>

			<div class="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2 min-w-0 flex-1 sm:flex-initial">
				<label for="season-select" class="text-accent-2 text-xs font-semibold shrink-0">Arteta era:</label>
				<select
					id="season-select"
					bind:value={selectedSeason}
					onchange={applyFilters}
					class="w-full sm:w-72 min-w-0 max-w-full min-h-[44px] bg-paper-2 border border-rule text-ink font-semibold rounded-card px-3 text-sm"
				>
					<option value="all">All seasons (2019 to present)</option>
					{#each seasons as s (s.id)}
						<option value={s.id}>
							{s.label}: {s.headline}
						</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	<!-- Arteta Era Milestone Callout -->
	{#if currentSeasonDetail}
		<div class="bg-paper-2 border-t-2 border-rule-2 p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
			<div class="space-y-1.5">
				<div class="flex items-baseline gap-3 flex-wrap">
					<span class="num text-xs font-semibold text-accent-2">{currentSeasonDetail.label}</span>
					<h3 class="font-bold text-ink text-base card-headline">{currentSeasonDetail.headline}</h3>
				</div>
				<p class="text-ink-2 text-sm">{currentSeasonDetail.arteta_milestone}</p>
			</div>
			{#if currentSeasonDetail.is_current}
				<span role="status" class="text-xs font-semibold text-success shrink-0">
					Active campaign
				</span>
			{/if}
		</div>
	{/if}

	{#if matchesError}
		<StateBanner
			variant="error"
			title="Match ledger unavailable"
			message={matchesError}
			busy={isLoading}
			onretry={applyFilters}
		/>
	{/if}

	<!-- Result Count -->
	<div role="status" aria-live="polite" class="flex items-center justify-between text-xs text-muted num">
		<span>{isLoading ? 'Updating match ledger…' : `${matches.length} matches shown`}</span>
		<span>Times shown in local timezone</span>
	</div>

	<!-- Matches Ledger -->
	{#if isLoading && matches.length === 0}
		<div role="status" class="py-12 text-muted text-sm">
			Loading Arsenal matches…
		</div>
	{:else if matches.length === 0 && !matchesError}
		<StateBanner
			variant="empty"
			title="No Arsenal matches found"
			message="No fixtures matched the selected competition, status, or season filter."
			retryLabel="Reset filters"
			onretry={resetFilters}
		/>
	{:else if matches.length > 0}
		{#snippet matchRow(match: Match)}
			<div class="py-3.5 px-3 flex flex-col gap-3 hover:bg-paper-3/50 transition-colors">
				<div class="flex items-center justify-between gap-2 text-xs text-muted">
					<div class="flex items-center gap-2">
						<span class="font-semibold text-ink-2">{match.competition_id || 'PL'}</span>
						{#if match.matchday}
							<span class="num">MD {match.matchday}</span>
						{/if}
					</div>
					<time class="num">{formatMatchDateTime(match.utc_date)}</time>
				</div>

				<a
					href="/matches/{encodeURIComponent(match.id)}"
					class="group grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2 sm:gap-3 min-w-0"
				>
					<div class="flex items-center justify-end gap-2 text-right min-w-0">
						<span class="text-xs sm:text-sm font-semibold group-hover:text-accent-text transition-colors truncate {match.home_team_id === 'arsenal' ? 'text-ink' : 'text-ink-2'}">
							{match.home_team_name}
						</span>
						{#if match.home_team_crest && !failedCrests[`row-home-${match.id}`]}
							<img
								src={match.home_team_crest}
								alt=""
								width="20"
								height="20"
								class="w-5 h-5 object-contain shrink-0"
								onerror={() => (failedCrests = { ...failedCrests, [`row-home-${match.id}`]: true })}
							/>
						{/if}
					</div>

					<div class="min-w-[64px] text-center shrink-0">
						{#if match.status === 'FINISHED' && match.home_score !== null && match.home_score !== undefined}
							<span class="num font-outlier font-semibold text-sm text-ink px-2.5 py-1 rounded-card bg-paper-3 border border-rule">
								{match.home_score} : {match.away_score}
							</span>
						{:else}
							<span class="text-xs font-semibold text-accent-2 px-2 py-1 rounded-card bg-paper-3">
								vs
							</span>
						{/if}
					</div>

					<div class="flex items-center justify-start gap-2 text-left min-w-0">
						{#if match.away_team_crest && !failedCrests[`row-away-${match.id}`]}
							<img
								src={match.away_team_crest}
								alt=""
								width="20"
								height="20"
								class="w-5 h-5 object-contain shrink-0"
								onerror={() => (failedCrests = { ...failedCrests, [`row-away-${match.id}`]: true })}
							/>
						{/if}
						<span class="text-xs sm:text-sm font-semibold group-hover:text-accent-text transition-colors truncate {match.away_team_id === 'arsenal' ? 'text-ink' : 'text-ink-2'}">
							{match.away_team_name}
						</span>
					</div>
				</a>

				<div class="flex items-center justify-between gap-2 text-xs">
					<span class="text-muted truncate">{match.venue || match.competition_name || ''}</span>
					<div class="flex items-center gap-2 shrink-0">
						<a
							href="/matches/{encodeURIComponent(match.id)}"
							class="inline-flex items-center min-h-[36px] px-2.5 rounded-card border border-rule bg-paper hover:bg-paper-3 font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
						>
							Match center
						</a>
						{#if match.status !== 'FINISHED'}
							<a
								href="/predictions"
								class="inline-flex items-center min-h-[36px] px-2.5 rounded-card bg-accent text-accent-ink hover:opacity-90 font-semibold transition-opacity whitespace-nowrap"
							>
								Predict
							</a>
						{/if}
					</div>
				</div>
			</div>
		{/snippet}

		{#if activeTab === 'ALL'}
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start {isLoading ? 'opacity-70 transition-opacity' : ''}">
				<!-- Left: Previous Results (latest result at the very top) -->
				<section class="rounded-card border border-rule bg-paper-2 overflow-hidden">
					<div class="px-4 py-3 border-b-2 border-rule-2 flex items-center justify-between">
						<h2 class="text-base font-bold text-ink">Previous results</h2>
						<span class="num text-xs text-muted">{previousResults.length} matches · Latest first</span>
					</div>
					{#if previousResults.length === 0}
						<p class="p-6 text-sm text-muted">No completed results match the current filter.</p>
					{:else}
						<div class="divide-y divide-rule">
							{#each previousResults as match (match.id)}
								{@render matchRow(match)}
							{/each}
						</div>
					{/if}
				</section>

				<!-- Right: Upcoming Fixtures (immediate next match at the very top) -->
				<section class="rounded-card border border-rule bg-paper-2 overflow-hidden">
					<div class="px-4 py-3 border-b-2 border-rule-2 flex items-center justify-between">
						<h2 class="text-base font-bold text-ink">Upcoming fixtures</h2>
						<span class="num text-xs text-accent-2">{upcomingFixtures.length} matches · Next match first</span>
					</div>
					{#if upcomingFixtures.length === 0}
						<p class="p-6 text-sm text-muted">No upcoming fixtures match the current filter.</p>
					{:else}
						<div class="divide-y divide-rule">
							{#each upcomingFixtures as match (match.id)}
								{@render matchRow(match)}
							{/each}
						</div>
					{/if}
				</section>
			</div>
		{:else}
			{@const singleList = activeTab === 'FINISHED' ? previousResults : upcomingFixtures}
			<div class="rounded-card border border-rule bg-paper-2 divide-y divide-rule {isLoading ? 'opacity-70 transition-opacity' : ''}">
				{#each singleList as match (match.id)}
					{@render matchRow(match)}
				{/each}
			</div>
		{/if}
	{/if}

	<!-- Data Provenance / Sync Footer -->
	{#if syncStatus}
		<div class="pt-2 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-muted gap-2">
			<div>
				Source: <span class="text-ink-2 font-semibold">{syncStatus.source}</span>
			</div>
			<div class="num">
				Last synced: <span class="text-ink-2">{formatMatchDateTime(syncStatus.latest_sync || '')}</span>
			</div>
		</div>
	{/if}
</div>
