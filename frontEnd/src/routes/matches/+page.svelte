<script lang="ts">
	import { fetchMatches } from '$lib/api/football';
	import type { Match, MatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let activeTab = $state<'ALL' | 'SCHEDULED' | 'FINISHED'>('ALL');
	let selectedComp = $state<string>('ALL');
	let selectedSeason = $state<string>('all');
	let isLoading = $state(false);

	let matches = $state<Match[]>([]);
	let summary = $state<MatchSummary | null>(null);
	let syncStatus = $derived(data.syncStatus);
	let seasons = $derived(data.seasons || []);
	let currentSeasonDetail = $derived(
		selectedSeason !== 'all' ? seasons.find((s) => s.id === selectedSeason) : null
	);

	$effect(() => {
		matches = data.initialMatches;
		summary = data.initialSummary;
		selectedSeason = data.activeSeasonId || 'all';
	});

	async function applyFilters() {
		isLoading = true;
		try {
			matches = await fetchMatches({
				club_id: 'arsenal',
				competition_id: selectedComp !== 'ALL' ? selectedComp : undefined,
				status: activeTab !== 'ALL' ? activeTab : undefined,
				season_id: selectedSeason !== 'all' ? selectedSeason : undefined
			});
		} finally {
			isLoading = false;
		}
	}

	function formatDate(utcString: string): string {
		try {
			const d = new Date(utcString);
			return d.toLocaleDateString(undefined, {
				weekday: 'short',
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
	<title>Arsenal Match Schedule & Results | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12">
	<!-- Page Header -->
	<div class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-2 border-rule-2 pb-8">
		<div class="space-y-3">
			<h1>Arsenal match ledger</h1>
			<p class="lead text-ink-2">
				Mikel Arteta’s Premier League and Champions League campaigns with verified scorelines and venues.
			</p>
		</div>

		<div class="flex items-center gap-3">
			<a
				href="/predictions"
				class="inline-flex items-center h-10 px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 font-semibold text-sm transition-opacity whitespace-nowrap"
			>
				Match predictor
			</a>
			<a
				href="/board"
				class="inline-flex items-center h-10 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 font-semibold text-sm text-ink transition-colors whitespace-nowrap"
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
				<h2 class="text-base font-semibold text-ink">Recent form (last 5)</h2>
				<div class="flex items-center gap-2">
					{#if summary.recent_form.length > 0}
						{#each summary.recent_form as res}
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
			<div class="md:col-span-8 md:border-l md:border-rule md:pl-8 space-y-3">
				<h2 class="text-base font-semibold text-ink">Next scheduled fixture</h2>
				{#if summary.next_fixture}
					<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
						<div class="flex items-center gap-4">
							<div class="flex items-center gap-2">
								{#if summary.next_fixture.home_team_crest}
									<img src={summary.next_fixture.home_team_crest} alt="" width="24" height="24" class="w-6 h-6 object-contain" />
								{/if}
								<span class="text-base font-bold text-ink">{summary.next_fixture.home_team_name}</span>
							</div>
							<span class="text-xs text-muted px-2 py-0.5 bg-paper-3 rounded-card">vs</span>
							<div class="flex items-center gap-2">
								{#if summary.next_fixture.away_team_crest}
									<img src={summary.next_fixture.away_team_crest} alt="" width="24" height="24" class="w-6 h-6 object-contain" />
								{/if}
								<span class="text-base font-bold text-ink">{summary.next_fixture.away_team_name}</span>
							</div>
						</div>
						<div class="sm:text-right">
							<div class="num text-sm font-semibold text-accent-2">{formatDate(summary.next_fixture.utc_date)}</div>
							<div class="text-xs text-muted">{summary.next_fixture.venue || summary.next_fixture.competition_name}</div>
						</div>
					</div>
				{:else}
					<p class="text-sm text-muted">No upcoming fixtures scheduled in active window.</p>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Filter Controls -->
	<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-rule pb-5">
		<!-- Tab Switcher -->
		<div class="flex items-center gap-2 flex-wrap">
			<button
				type="button"
				onclick={() => { activeTab = 'ALL'; applyFilters(); }}
				class="h-9 px-3.5 rounded-card transition-colors text-sm font-semibold border whitespace-nowrap {activeTab === 'ALL' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				All matches
			</button>
			<button
				type="button"
				onclick={() => { activeTab = 'SCHEDULED'; applyFilters(); }}
				class="h-9 px-3.5 rounded-card transition-colors text-sm font-semibold border whitespace-nowrap {activeTab === 'SCHEDULED' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Upcoming fixtures
			</button>
			<button
				type="button"
				onclick={() => { activeTab = 'FINISHED'; applyFilters(); }}
				class="h-9 px-3.5 rounded-card transition-colors text-sm font-semibold border whitespace-nowrap {activeTab === 'FINISHED' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Completed results
			</button>
		</div>

		<!-- Competition & Season Dropdowns -->
		<div class="flex items-center gap-4 flex-wrap text-sm">
			<div class="flex items-center gap-2">
				<label for="comp-select" class="text-muted text-xs">Competition:</label>
				<select
					id="comp-select"
					bind:value={selectedComp}
					onchange={applyFilters}
					class="h-9 bg-paper-2 border border-rule text-ink rounded-card px-3 text-sm"
				>
					<option value="ALL">All competitions</option>
					<option value="PL">Premier League</option>
					<option value="CL">Champions League</option>
				</select>
			</div>

			<div class="flex items-center gap-2">
				<label for="season-select" class="text-accent-2 text-xs font-semibold">Arteta era:</label>
				<select
					id="season-select"
					bind:value={selectedSeason}
					onchange={applyFilters}
					class="h-9 bg-paper-2 border border-rule text-ink font-semibold rounded-card px-3 text-sm"
				>
					<option value="all">All seasons (2019 to present)</option>
					{#each seasons as s}
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
				<div class="flex items-baseline gap-3">
					<span class="num text-xs font-semibold text-accent-2">{currentSeasonDetail.label}</span>
					<h3 class="font-bold text-ink text-base">{currentSeasonDetail.headline}</h3>
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

	<!-- Matches Ledger -->
	{#if isLoading}
		<div class="py-12 text-muted text-sm">
			Loading Arsenal matches…
		</div>
	{:else if matches.length === 0}
		<div class="border-t border-rule pt-8">
			<p class="text-sm text-ink-2 font-semibold">No Arsenal matches found for the selected filter.</p>
		</div>
	{:else}
		<div class="divide-y divide-rule border-y border-rule">
			{#each matches as match}
				<div class="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-paper-2 px-3 transition-colors">
					<!-- Date & Competition info -->
					<div class="min-w-[180px] space-y-0.5">
						<div class="flex items-center gap-2 text-xs text-muted">
							<span class="font-semibold text-ink-2">{match.competition_id || 'PL'}</span>
							{#if match.matchday}
								<span class="num">Matchday {match.matchday}</span>
							{/if}
						</div>
						<time class="num block text-xs text-muted">
							{formatDate(match.utc_date)}
						</time>
					</div>

					<!-- Teams & Score / Time -->
					<div class="flex-1 flex items-center justify-center gap-6">
						<!-- Home Team -->
						<div class="flex-1 flex items-center justify-end gap-2.5 text-right">
							<span class="text-sm font-semibold {match.home_team_id === 'arsenal' ? 'text-ink' : 'text-ink-2'}">
								{match.home_team_name}
							</span>
							{#if match.home_team_crest}
								<img src={match.home_team_crest} alt="" width="24" height="24" class="w-6 h-6 object-contain" />
							{/if}
						</div>

						<!-- Score / Status Box -->
						<div class="min-w-[96px] text-center">
							{#if match.status === 'FINISHED' && match.home_score !== null && match.home_score !== undefined}
								<div class="num font-outlier font-semibold text-base text-ink px-3 py-1 rounded-card bg-paper-3">
									{match.home_score} : {match.away_score}
								</div>
								<div class="text-xs text-muted mt-0.5">Full time</div>
							{:else}
								<div class="text-xs font-semibold text-accent-2 px-2.5 py-1 rounded-card bg-paper-3">
									Upcoming
								</div>
							{/if}
						</div>

						<!-- Away Team -->
						<div class="flex-1 flex items-center justify-start gap-2.5 text-left">
							{#if match.away_team_crest}
								<img src={match.away_team_crest} alt="" width="24" height="24" class="w-6 h-6 object-contain" />
							{/if}
							<span class="text-sm font-semibold {match.away_team_id === 'arsenal' ? 'text-ink' : 'text-ink-2'}">
								{match.away_team_name}
							</span>
						</div>
					</div>

					<!-- Venue & Actions -->
					<div class="min-w-[180px] flex items-center justify-end gap-4 text-right">
						{#if match.venue}
							<span class="text-xs text-muted truncate max-w-[130px] hidden lg:inline" title={match.venue}>
								{match.venue}
							</span>
						{/if}
						{#if match.status === 'FINISHED'}
							<a
								href="/terrace"
								class="inline-flex items-center h-8 px-3 rounded-card border border-rule bg-paper-3 hover:bg-paper text-xs font-semibold text-ink transition-colors whitespace-nowrap"
							>
								Debate
							</a>
						{:else}
							<a
								href="/predictions"
								class="inline-flex items-center h-8 px-3 rounded-card bg-accent text-accent-ink hover:opacity-90 text-xs font-semibold transition-opacity whitespace-nowrap"
							>
								Predict
							</a>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Data Provenance / Sync Footer -->
	{#if syncStatus}
		<div class="pt-2 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-muted gap-2">
			<div>
				Source: <span class="text-ink-2 font-semibold">{syncStatus.source}</span>
			</div>
			<div class="num">
				Last synced: <span class="text-ink-2">{formatDate(syncStatus.latest_sync || '')}</span>
			</div>
		</div>
	{/if}
</div>
