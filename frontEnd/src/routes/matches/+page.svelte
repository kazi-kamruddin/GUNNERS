<script lang="ts">
	import { fetchMatches, fetchMatchSummary } from '$lib/api/football';
	import type { Match, MatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Reactive filter states
	let activeTab = $state<'ALL' | 'SCHEDULED' | 'FINISHED'>('ALL');
	let selectedComp = $state<string>('ALL');
	let isLoading = $state(false);

	let matches = $state<Match[]>([]);
	let summary = $state<MatchSummary | null>(null);
	let syncStatus = $derived(data.syncStatus);

	$effect(() => {
		matches = data.initialMatches;
		summary = data.initialSummary;
	});

	async function applyFilters() {
		isLoading = true;
		try {
			matches = await fetchMatches({
				club_id: 'arsenal',
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
</script>

<svelte:head>
	<title>Arsenal Match Schedule & Results | GUNNERS</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
	<!-- Page Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-red-900/30 pb-6">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-red-950/70 text-red-400 border border-red-800/40 font-mono">
				Emirates Campaign Hub
			</div>
			<h1 class="text-3xl font-black tracking-tight text-white uppercase flex items-center gap-2.5">
				<span>Arsenal Match Schedule & Results</span>
			</h1>
			<p class="text-sm text-gray-400 mt-1">
				Mikel Arteta's Premier League & UEFA Champions League campaigns with verified scorelines, venues, and tactical links.
			</p>
		</div>

		<div class="flex items-center gap-2">
			<a
				href="/predictions"
				class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 font-bold text-xs text-white transition shadow-sm flex items-center gap-1.5"
			>
				<span>🎯 Match Predictor</span>
			</a>
			<a
				href="/board"
				class="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2430] font-semibold text-xs text-gray-200 transition"
			>
				<span>📋 Lineup Studio</span>
			</a>
		</div>
	</div>

	<!-- Form & Overview Card -->
	{#if summary}
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<!-- Recent Form Card -->
			<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f]">
				<h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Arsenal Form (Last 5)</h2>
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
			<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] md:col-span-2">
				<h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Next Scheduled Match</h2>
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
				class="px-3 py-1.5 rounded transition font-semibold {activeTab === 'ALL' ? 'bg-red-600 text-white shadow-sm' : 'text-gray-400 hover:text-white'}"
			>
				All Matches
			</button>
			<button
				type="button"
				onclick={() => { activeTab = 'SCHEDULED'; applyFilters(); }}
				class="px-3 py-1.5 rounded transition font-semibold {activeTab === 'SCHEDULED' ? 'bg-red-600 text-white shadow-sm' : 'text-gray-400 hover:text-white'}"
			>
				Upcoming Fixtures
			</button>
			<button
				type="button"
				onclick={() => { activeTab = 'FINISHED'; applyFilters(); }}
				class="px-3 py-1.5 rounded transition font-semibold {activeTab === 'FINISHED' ? 'bg-red-600 text-white shadow-sm' : 'text-gray-400 hover:text-white'}"
			>
				Completed Results
			</button>
		</div>

		<!-- Competition Dropdown -->
		<div class="flex items-center gap-2 text-xs">
			<label for="comp-select" class="text-gray-400">Competition:</label>
			<select
				id="comp-select"
				bind:value={selectedComp}
				onchange={applyFilters}
				class="bg-[#12161f] border border-[#1e2430] text-white rounded px-2.5 py-1.5 focus:outline-none focus:border-red-500"
			>
				<option value="ALL">All Competitions</option>
				<option value="PL">Premier League</option>
				<option value="CL">Champions League</option>
			</select>
		</div>
	</div>

	<!-- Matches List -->
	{#if isLoading}
		<div class="py-12 text-center text-gray-500 text-sm">
			Loading Arsenal matches...
		</div>
	{:else if matches.length === 0}
		<div class="py-12 text-center border border-dashed border-[#1e2430] rounded-xl bg-[#12161f]/50">
			<p class="text-sm text-gray-400 font-bold">No Arsenal matches found for the selected filter.</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each matches as match}
				<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] hover:border-red-900/50 transition flex flex-col md:flex-row md:items-center justify-between gap-4">
					<!-- Date & Competition info -->
					<div class="min-w-[140px]">
						<div class="flex items-center gap-2">
							<span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-black/40 border border-[#1e2430] text-gray-300">
								{match.competition_id || 'PL'}
							</span>
							{#if match.matchday}
								<span class="text-[10px] text-gray-400 font-mono">Matchday {match.matchday}</span>
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
							<span class="text-sm font-bold {match.home_team_id === 'arsenal' ? 'text-red-400' : 'text-gray-300'}">
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
									UPCOMING
								</div>
							{/if}
						</div>

						<!-- Away Team -->
						<div class="flex-1 flex items-center justify-start gap-2 text-left">
							{#if match.away_team_crest}
								<img src={match.away_team_crest} alt="" class="w-6 h-6 object-contain" />
							{/if}
							<span class="text-sm font-bold {match.away_team_id === 'arsenal' ? 'text-red-400' : 'text-gray-300'}">
								{match.away_team_name}
							</span>
						</div>
					</div>

					<!-- Venue & Actions -->
					<div class="min-w-[150px] flex items-center justify-end gap-3 text-right">
						{#if match.venue}
							<span class="text-[11px] text-gray-400 truncate max-w-[130px] hidden lg:inline font-mono" title={match.venue}>
								📍 {match.venue}
							</span>
						{/if}
						{#if match.status === 'FINISHED'}
							<a
								href="/terrace"
								class="text-xs font-semibold px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-[#1e2430] transition"
							>
								Debate
							</a>
						{:else}
							<a
								href="/predictions"
								class="text-xs font-semibold px-2.5 py-1 rounded bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30 transition"
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
		<div class="border-t border-[#1e2430] pt-4 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-gray-500 gap-2">
			<div>
				Source: <span class="text-gray-400 font-mono">{syncStatus.source}</span>
			</div>
			<div>
				Last Synced: <span class="text-gray-400 font-mono">{formatDate(syncStatus.latest_sync || '')}</span>
			</div>
		</div>
	{/if}
</div>
