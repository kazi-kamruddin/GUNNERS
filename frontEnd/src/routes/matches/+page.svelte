<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { fetchMatches, fetchMatchSummary } from '$lib/api/football';
	import type { Match, MatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Reactive filter states
	let selectedClubId = $state(themeState.viewingClubId);
	let activeTab = $state<'ALL' | 'SCHEDULED' | 'FINISHED'>('ALL');
	let selectedComp = $state<string>('ALL');
	let isLoading = $state(false);

	let matches = $state<Match[]>([]);
	let summary = $state<MatchSummary | null>(null);
	let syncStatus = $derived(data.syncStatus);

	const clubsList = Object.values(CLUBS);

	$effect(() => {
		selectedClubId = data.initialClubId || themeState.viewingClubId;
		matches = data.initialMatches;
		summary = data.initialSummary;
	});

	// Sync when global viewing club changes
	$effect(() => {
		if (themeState.viewingClubId !== selectedClubId) {
			selectClub(themeState.viewingClubId);
		}
	});

	async function selectClub(clubId: string) {
		selectedClubId = clubId;
		themeState.setViewingClub(clubId);
		isLoading = true;
		try {
			const [newMatches, newSummary] = await Promise.all([
				fetchMatches({
					club_id: clubId,
					competition_id: selectedComp !== 'ALL' ? selectedComp : undefined,
					status: activeTab !== 'ALL' ? activeTab : undefined
				}),
				fetchMatchSummary(clubId)
			]);
			matches = newMatches;
			summary = newSummary;
		} finally {
			isLoading = false;
		}
	}

	async function applyFilters() {
		isLoading = true;
		try {
			matches = await fetchMatches({
				club_id: selectedClubId,
				competition_id: selectedComp !== 'ALL' ? selectedComp : undefined,
				status: activeTab !== 'ALL' ? activeTab : undefined
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

	let currentClubObj = $derived(CLUBS[selectedClubId] || CLUBS['arsenal']);
</script>

<svelte:head>
	<title>Matches & Fixtures | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
	<!-- Page Header & Club Switcher -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e2430] pb-6">
		<div>
			<div class="flex items-center gap-3">
				<div class="w-3.5 h-3.5 rounded-full" style="background-color: {currentClubObj.primary_color}"></div>
				<h1 class="text-2xl font-black tracking-tight text-white uppercase">
					{currentClubObj.name} Matches & Fixtures
				</h1>
			</div>
			<p class="text-sm text-gray-400 mt-1">
				Real-time sync from football-data.org. Showing 2024-2025 season schedules and verified results.
			</p>
		</div>

		<!-- Quick Club Pills -->
		<div class="flex items-center gap-2 flex-wrap">
			{#each clubsList as club}
				<button
					type="button"
					onclick={() => selectClub(club.id)}
					class="px-3 py-1.5 rounded text-xs font-bold transition flex items-center gap-1.5 border {selectedClubId === club.id ? 'bg-white/10 text-white border-white/20' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#12161f]'}"
				>
					<span class="w-2 h-2 rounded-full" style="background-color: {club.primary_color}"></span>
					<span>{club.short_name}</span>
				</button>
			{/each}
		</div>
	</div>

	<!-- Form & Overview Card -->
	{#if summary}
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<!-- Recent Form Card -->
			<div class="p-5 rounded-lg border border-[#1e2430] bg-[#12161f]">
				<h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Recent Form (Last 5)</h2>
				<div class="flex items-center gap-2">
					{#if summary.recent_form.length > 0}
						{#each summary.recent_form as res}
							<span
								class="w-7 h-7 rounded flex items-center justify-center font-bold text-xs {res === 'W' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : res === 'D' ? 'bg-amber-950 text-amber-400 border border-amber-800' : 'bg-red-950 text-red-400 border border-red-800'}"
							>
								{res}
							</span>
						{/each}
					{:else}
						<span class="text-xs text-gray-500">No recent completed matches</span>
					{/if}
				</div>
				<div class="mt-3 text-xs text-gray-500 flex gap-4">
					<span>Completed: <strong class="text-white">{summary.total_completed}</strong></span>
					<span>Scheduled: <strong class="text-white">{summary.total_scheduled}</strong></span>
				</div>
			</div>

			<!-- Next Fixture Quick View -->
			<div class="p-5 rounded-lg border border-[#1e2430] bg-[#12161f] md:col-span-2">
				<h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Next Fixture</h2>
				{#if summary.next_fixture}
					<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
						<div class="flex items-center gap-4">
							<div class="flex items-center gap-2">
								{#if summary.next_fixture.home_team_crest}
									<img src={summary.next_fixture.home_team_crest} alt="" class="w-6 h-6 object-contain" />
								{/if}
								<span class="text-sm font-bold text-white">{summary.next_fixture.home_team_name}</span>
							</div>
							<span class="text-xs font-mono text-gray-500 uppercase px-2 py-0.5 rounded bg-black/40 border border-[#1e2430]">VS</span>
							<div class="flex items-center gap-2">
								{#if summary.next_fixture.away_team_crest}
									<img src={summary.next_fixture.away_team_crest} alt="" class="w-6 h-6 object-contain" />
								{/if}
								<span class="text-sm font-bold text-white">{summary.next_fixture.away_team_name}</span>
							</div>
						</div>
						<div class="text-right">
							<div class="text-xs font-semibold text-amber-400">{formatDate(summary.next_fixture.utc_date)}</div>
							<div class="text-[11px] text-gray-400">{summary.next_fixture.venue || summary.next_fixture.competition_name}</div>
						</div>
					</div>
				{:else}
					<p class="text-xs text-gray-500">No upcoming fixtures scheduled in active window.</p>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Filter Controls -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1e2430] pb-4">
		<!-- Tab Switcher -->
		<div class="flex items-center gap-1 bg-[#12161f] p-1 rounded-lg border border-[#1e2430] text-xs">
			<button
				type="button"
				onclick={() => { activeTab = 'ALL'; applyFilters(); }}
				class="px-3 py-1.5 rounded transition font-semibold {activeTab === 'ALL' ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white'}"
			>
				All Matches
			</button>
			<button
				type="button"
				onclick={() => { activeTab = 'SCHEDULED'; applyFilters(); }}
				class="px-3 py-1.5 rounded transition font-semibold {activeTab === 'SCHEDULED' ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white'}"
			>
				Upcoming Fixtures
			</button>
			<button
				type="button"
				onclick={() => { activeTab = 'FINISHED'; applyFilters(); }}
				class="px-3 py-1.5 rounded transition font-semibold {activeTab === 'FINISHED' ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white'}"
			>
				Results
			</button>
		</div>

		<!-- Competition Dropdown -->
		<div class="flex items-center gap-2 text-xs">
			<label for="comp-select" class="text-gray-400">Competition:</label>
			<select
				id="comp-select"
				bind:value={selectedComp}
				onchange={applyFilters}
				class="bg-[#12161f] border border-[#1e2430] text-white rounded px-2.5 py-1.5 focus:outline-none focus:border-gray-500"
			>
				<option value="ALL">All Competitions</option>
				<option value="PL">Premier League</option>
				<option value="PD">La Liga</option>
				<option value="SA">Serie A</option>
				<option value="CL">Champions League</option>
			</select>
		</div>
	</div>

	<!-- Matches List -->
	{#if isLoading}
		<div class="py-12 text-center text-gray-500 text-sm">
			Loading matches...
		</div>
	{:else if matches.length === 0}
		<div class="py-12 text-center border border-dashed border-[#1e2430] rounded-lg">
			<p class="text-sm text-gray-400">No matches found for the selected filters.</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each matches as match}
				<div class="p-4 rounded-lg border border-[#1e2430] bg-[#12161f] hover:border-gray-700 transition flex flex-col md:flex-row md:items-center justify-between gap-4">
					<!-- Date & Competition info -->
					<div class="min-w-[140px]">
						<div class="flex items-center gap-2">
							<span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-black/40 border border-[#1e2430] text-gray-300">
								{match.competition_id || 'MATCH'}
							</span>
							{#if match.matchday}
								<span class="text-[10px] text-gray-400">MD {match.matchday}</span>
							{/if}
						</div>
						<div class="text-xs text-gray-400 mt-1 font-mono">
							{formatDate(match.utc_date)}
						</div>
					</div>

					<!-- Teams & Score / Time -->
					<div class="flex-1 flex items-center justify-center gap-6">
						<!-- Home Team -->
						<div class="flex-1 flex items-center justify-end gap-2 text-right">
							<span class="text-sm font-bold {match.home_team_id === selectedClubId ? 'text-white' : 'text-gray-300'}">
								{match.home_team_name}
							</span>
							{#if match.home_team_crest}
								<img src={match.home_team_crest} alt="" class="w-6 h-6 object-contain" />
							{/if}
						</div>

						<!-- Score / Status Box -->
						<div class="min-w-[80px] text-center">
							{#if match.status === 'FINISHED' && match.home_score !== null && match.home_score !== undefined}
								<div class="text-base font-mono font-black text-white px-2.5 py-1 rounded bg-black/60 border border-[#1e2430]">
									{match.home_score} - {match.away_score}
								</div>
								<div class="text-[9px] text-emerald-400 uppercase mt-0.5 font-bold">Final</div>
							{:else}
								<div class="text-xs font-mono text-amber-400 px-2 py-1 rounded bg-amber-500/10 border border-amber-500/20 font-bold">
									SCHEDULED
								</div>
							{/if}
						</div>

						<!-- Away Team -->
						<div class="flex-1 flex items-center justify-start gap-2 text-left">
							{#if match.away_team_crest}
								<img src={match.away_team_crest} alt="" class="w-6 h-6 object-contain" />
							{/if}
							<span class="text-sm font-bold {match.away_team_id === selectedClubId ? 'text-white' : 'text-gray-300'}">
								{match.away_team_name}
							</span>
						</div>
					</div>

					<!-- Venue & Actions -->
					<div class="min-w-[150px] flex items-center justify-end gap-3 text-right">
						{#if match.venue}
							<span class="text-[11px] text-gray-500 truncate max-w-[120px] hidden lg:inline" title={match.venue}>
								{match.venue}
							</span>
						{/if}
						<a
							href="/lab"
							class="text-xs font-semibold px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-[#1e2430] transition"
							title="Analyze team performance in Data Lab"
						>
							Analyze
						</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Data Provenance / Sync Footer -->
	{#if syncStatus}
		<div class="border-t border-[#1e2430] pt-4 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-gray-500 gap-2">
			<div>
				Source: <span class="text-gray-400">{syncStatus.source}</span> · Free Tier Quota Aware (10 req/min)
			</div>
			<div>
				Last Synced: <span class="text-gray-400 font-mono">{formatDate(syncStatus.latest_sync || '')}</span>
			</div>
		</div>
	{/if}
</div>
