<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { queryAnalytics, createInsight, fetchInsights } from '$lib/api/football';
	import type { AnalyticsResponse, Insight } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Modes: single or comparison
	let mode = $state<'single' | 'comparison'>('single');
	let team1 = $state<string>('arsenal');
	let team2 = $state<string>('real-madrid');
	let metric = $state<string>('win_rate');
	let venue = $state<string>('all');

	let loading = $state(false);
	let result = $state<AnalyticsResponse | null>(null);
	let insights = $state<Insight[]>([]);

	$effect(() => {
		mode = data.initialTeamIds.length > 1 ? 'comparison' : 'single';
		team1 = data.initialTeamIds[0] || 'arsenal';
		team2 = data.initialTeamIds[1] || 'real-madrid';
		metric = data.initialMetric || 'win_rate';
		venue = data.initialVenue || 'all';
		result = data.initialResult;
		insights = data.insights || [];
	});

	// Insight creation modal state
	let isModalOpen = $state(false);
	let insightTitle = $state('');
	let insightDesc = $state('');
	let isSavingInsight = $state(false);
	let toastMessage = $state<string | null>(null);

	const clubList = Object.values(CLUBS);

	const metricsList = [
		{ id: 'win_rate', label: 'Win Rate (%)' },
		{ id: 'goals_per_match', label: 'Goals Per Match' },
		{ id: 'points_per_game', label: 'Points Per Game (PPG)' },
		{ id: 'goal_difference', label: 'Goal Difference' },
		{ id: 'clean_sheet_rate', label: 'Clean Sheet Rate (%)' },
		{ id: 'loss_rate', label: 'Loss Rate (%)' }
	];

	// Run analytics query
	async function runQuery() {
		loading = true;
		const team_ids = mode === 'single' ? [team1] : [team1, team2];
		try {
			result = await queryAnalytics({
				metric,
				team_ids,
				venue
			});
			updateUrlState(team_ids);
		} finally {
			loading = false;
		}
	}

	function updateUrlState(team_ids: string[]) {
		if (typeof window !== 'undefined') {
			const url = new URL(window.location.href);
			url.searchParams.set('metric', metric);
			url.searchParams.set('teams', team_ids.join(','));
			url.searchParams.set('venue', venue);
			window.history.replaceState({}, '', url.toString());
		}
	}

	function copyShareLink() {
		if (typeof window !== 'undefined') {
			navigator.clipboard.writeText(window.location.href);
			showToast('Reproducible analysis link copied to clipboard!');
		}
	}

	function openCreateModal() {
		if (!result || result.series.length === 0) return;
		const t1 = result.series[0];
		if (result.series.length === 1) {
			insightTitle = `${t1.team_name} ${getMetricLabel(metric)}: ${t1.metric_value} ${t1.unit} (${venue})`;
		} else {
			const t2 = result.series[1];
			insightTitle = `${t1.team_name} vs ${t2.team_name}: ${getMetricLabel(metric)} Comparison`;
		}
		insightDesc = `Computed across eligible completed matches (Venue filter: ${venue}).`;
		isModalOpen = true;
	}

	async function submitInsight() {
		if (!result || !insightTitle) return;
		isSavingInsight = true;
		try {
			const team_ids = mode === 'single' ? [team1] : [team1, team2];
			const newInsight = await createInsight({
				title: insightTitle,
				description: insightDesc,
				metric,
				team_ids,
				venue,
				chart_type: mode === 'single' ? 'bar' : 'comparison',
				author_name: data.profile?.display_name || 'Supporter',
				author_club_id: data.profile?.favorite_club_id || team1,
				snapshot: result
			});

			if (newInsight) {
				insights = [newInsight, ...insights];
				isModalOpen = false;
				showToast('Insight published successfully! Visible in community feed.');
			}
		} finally {
			isSavingInsight = false;
		}
	}

	function loadExistingInsight(ins: Insight) {
		metric = ins.metric;
		venue = ins.venue;
		if (ins.team_ids.length > 1) {
			mode = 'comparison';
			team1 = ins.team_ids[0];
			team2 = ins.team_ids[1];
		} else {
			mode = 'single';
			team1 = ins.team_ids[0];
		}
		result = ins.snapshot;
		updateUrlState(ins.team_ids);
		showToast(`Loaded insight: "${ins.title}"`);
	}

	function getMetricLabel(id: string): string {
		return metricsList.find((m) => m.id === id)?.label || id;
	}

	function showToast(msg: string) {
		toastMessage = msg;
		setTimeout(() => {
			toastMessage = null;
		}, 4000);
	}

	// Calculated helpers for comparative bars
	let maxMetricVal = $derived(
		result && result.series.length > 0
			? Math.max(...result.series.map((s) => Math.abs(s.metric_value)), 1)
			: 1
	);

	let deltaDiff = $derived.by(() => {
		if (!result || result.series.length < 2) return null;
		const s1 = result.series[0];
		const s2 = result.series[1];
		const diff = Math.round((s1.metric_value - s2.metric_value) * 10) / 10;
		if (diff === 0) return { leader: 'Tied', text: 'Equal performance' };
		const leaderName = diff > 0 ? s1.team_name : s2.team_name;
		return {
			leader: leaderName,
			text: `${leaderName} leads by ${Math.abs(diff)} ${s1.unit}`
		};
	});
</script>

<svelte:head>
	<title>The Data Lab | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
	<!-- Toast Notification -->
	{#if toastMessage}
		<div class="fixed bottom-6 right-6 z-50 bg-[#12161f] border border-emerald-500/40 text-emerald-300 px-4 py-3 rounded-lg shadow-xl text-xs flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-emerald-400"></span>
			<span>{toastMessage}</span>
		</div>
	{/if}

	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e2430] pb-6">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
				Verified Canonical Analytics
			</div>
			<h1 class="text-2xl font-black text-white uppercase tracking-tight">The Data Lab</h1>
			<p class="text-sm text-gray-400 mt-1">
				Generate reproducible, explainable football statistics and publish shareable insight charts.
			</p>
		</div>

		<!-- Action Bar -->
		<div class="flex items-center gap-2">
			<a
				href="/lab/historical"
				class="px-3.5 py-2 rounded-lg border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 text-xs text-amber-300 font-semibold transition flex items-center gap-1.5"
			>
				<span>StatsBomb 2D Pitch</span>
			</a>
			<button
				type="button"
				onclick={copyShareLink}
				class="px-3.5 py-2 rounded-lg border border-[#1e2430] bg-[#12161f] hover:border-gray-600 text-xs text-gray-300 hover:text-white font-medium transition flex items-center gap-1.5"
			>
				<span>Share Analysis Link</span>
			</button>
			{#if result && result.series.length > 0}
				<button
					type="button"
					onclick={openCreateModal}
					class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-xs text-white font-bold transition shadow-sm"
				>
					Save as Insight
				</button>
			{/if}
		</div>
	</div>

	<!-- Query Builder -->
	<div class="p-6 rounded-lg border border-[#1e2430] bg-[#12161f] space-y-4">
		<!-- Mode Switcher -->
		<div class="flex items-center justify-between border-b border-[#1e2430] pb-4">
			<div class="flex items-center gap-1 bg-[#0a0c10] p-1 rounded-lg border border-[#1e2430] text-xs">
				<button
					type="button"
					onclick={() => { mode = 'single'; runQuery(); }}
					class="px-3 py-1.5 rounded transition font-semibold {mode === 'single' ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white'}"
				>
					Single Club Analysis
				</button>
				<button
					type="button"
					onclick={() => { mode = 'comparison'; runQuery(); }}
					class="px-3 py-1.5 rounded transition font-semibold {mode === 'comparison' ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white'}"
				>
					Head-to-Head Comparison
				</button>
			</div>

			<span class="text-xs text-gray-500 hidden sm:inline font-mono">
				Coverage: 2024-2025 Regular Season
			</span>
		</div>

		<!-- Inputs Grid -->
		<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
			<!-- Primary Club -->
			<div>
				<label for="primary-club" class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
					{mode === 'single' ? 'Club' : 'Club A'}
				</label>
				<select
					id="primary-club"
					bind:value={team1}
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-gray-500"
				>
					{#each clubList as club}
						<option value={club.id}>{club.name}</option>
					{/each}
				</select>
			</div>

			<!-- Secondary Club (if comparison) -->
			{#if mode === 'comparison'}
				<div>
					<label for="secondary-club" class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
						Club B (Compare)
					</label>
					<select
						id="secondary-club"
						bind:value={team2}
						class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-gray-500"
					>
						{#each clubList as club}
							<option value={club.id} disabled={club.id === team1}>{club.name}</option>
						{/each}
					</select>
				</div>
			{/if}

			<!-- Metric -->
			<div>
				<label for="metric-select" class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
					Metric
				</label>
				<select
					id="metric-select"
					bind:value={metric}
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-gray-500"
				>
					{#each metricsList as m}
						<option value={m.id}>{m.label}</option>
					{/each}
				</select>
			</div>

			<!-- Venue Filter -->
			<div>
				<label for="venue-filter" class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
					Venue Filter
				</label>
				<select
					id="venue-filter"
					bind:value={venue}
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-gray-500"
				>
					<option value="all">All Matches</option>
					<option value="home">Home Matches Only</option>
					<option value="away">Away Matches Only</option>
				</select>
			</div>

			<!-- Run Query Button -->
			<div class="flex items-end {mode === 'single' ? 'sm:col-span-1' : ''}">
				<button
					type="button"
					onclick={runQuery}
					disabled={loading}
					class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-lg transition disabled:opacity-50"
				>
					{loading ? 'Computing...' : 'Calculate Analytics'}
				</button>
			</div>
		</div>
	</div>

	<!-- Output Display -->
	{#if loading}
		<div class="py-16 text-center text-gray-400 text-sm">
			Computing verified analytics across eligible completed records...
		</div>
	{:else if result && result.series.length > 0}
		{#if mode === 'single'}
			{@const s = result.series[0]}
			{@const clubObj = CLUBS[s.team_id] || CLUBS['arsenal']}
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- Big Metric Hero Card -->
				<div class="p-6 rounded-lg border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
					<div>
						<div class="flex items-center gap-2 mb-3">
							<span class="w-3 h-3 rounded-full" style="background-color: {clubObj.primary_color}"></span>
							<span class="text-xs font-mono font-bold uppercase text-gray-300">{s.team_name}</span>
						</div>
						<div class="text-5xl font-black text-white font-mono my-2">
							{s.metric_value} <span class="text-xl text-amber-400 font-normal">{s.unit}</span>
						</div>
						<p class="text-xs text-gray-500 font-mono mt-1">Formula: {result.formula}</p>
					</div>

					<!-- Visual Record Bar -->
					<div class="mt-6 pt-4 border-t border-[#1e2430]">
						<div class="flex items-center justify-between text-xs text-gray-400 mb-2">
							<span>Sample: <strong class="text-white">{s.matches_played} matches</strong></span>
							<div class="flex gap-2">
								<span class="text-emerald-400 font-bold">{s.wins}W</span>
								<span class="text-amber-400 font-bold">{s.draws}D</span>
								<span class="text-red-400 font-bold">{s.losses}L</span>
							</div>
						</div>
						{#if s.matches_played > 0}
							<div class="w-full h-2 rounded bg-black/50 overflow-hidden flex">
								<div style="width: {(s.wins / s.matches_played) * 100}%; background-color: #10b981;" title="Wins"></div>
								<div style="width: {(s.draws / s.matches_played) * 100}%; background-color: #f59e0b;" title="Draws"></div>
								<div style="width: {(s.losses / s.matches_played) * 100}%; background-color: #ef4444;" title="Losses"></div>
							</div>
						{/if}
					</div>
				</div>

				<!-- Statistical Breakdown -->
				<div class="lg:col-span-2 p-6 rounded-lg border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
					<div>
						<h2 class="text-sm font-bold text-white uppercase tracking-wider mb-4">Performance Breakdown</h2>
						<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
							<div class="p-3.5 rounded bg-[#0a0c10] border border-[#1e2430]">
								<span class="text-[11px] text-gray-500 uppercase">Goals For</span>
								<div class="text-xl font-bold text-white mt-1 font-mono">{s.goals_for}</div>
							</div>
							<div class="p-3.5 rounded bg-[#0a0c10] border border-[#1e2430]">
								<span class="text-[11px] text-gray-500 uppercase">Goals Against</span>
								<div class="text-xl font-bold text-white mt-1 font-mono">{s.goals_against}</div>
							</div>
							<div class="p-3.5 rounded bg-[#0a0c10] border border-[#1e2430]">
								<span class="text-[11px] text-gray-500 uppercase">Goal Diff</span>
								<div class="text-xl font-bold mt-1 font-mono {s.goal_difference >= 0 ? 'text-emerald-400' : 'text-red-400'}">
									{s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference}
								</div>
							</div>
							<div class="p-3.5 rounded bg-[#0a0c10] border border-[#1e2430]">
								<span class="text-[11px] text-gray-500 uppercase">Clean Sheets</span>
								<div class="text-xl font-bold text-white mt-1 font-mono">{s.clean_sheets || 0}</div>
							</div>
						</div>
					</div>

					<div class="mt-6 pt-4 border-t border-[#1e2430] text-[11px] text-gray-500 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
						<span>{result.disclaimer}</span>
						<span>Venue filter: <strong class="text-gray-300 capitalize">{result.venue_filter}</strong></span>
					</div>
				</div>
			</div>
		{:else}
			<!-- Head-to-Head Comparison View -->
			{@const t1 = result.series[0]}
			{@const t2 = result.series[1]}
			{@const club1 = CLUBS[t1.team_id] || CLUBS['arsenal']}
			{@const club2 = CLUBS[t2.team_id] || CLUBS['real-madrid']}

			<div class="space-y-6">
				<!-- Comparison Leader Banner -->
				{#if deltaDiff}
					<div class="p-4 rounded-lg bg-[#0a0c10] border border-[#1e2430] flex items-center justify-between flex-wrap gap-2">
						<div class="flex items-center gap-2">
							<span class="text-xs text-gray-400 font-mono">Metric Result:</span>
							<span class="text-sm font-bold text-amber-400">{deltaDiff.text}</span>
						</div>
						<div class="text-xs text-gray-500">
							Comparing <strong>{t1.team_name}</strong> vs <strong>{t2.team_name}</strong> ({result.venue_filter} matches)
						</div>
					</div>
				{/if}

				<!-- Side-by-Side Stat Cards -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<!-- Team 1 Card -->
					<div class="p-6 rounded-lg border border-[#1e2430] bg-[#12161f] space-y-4">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-2">
								<span class="w-3 h-3 rounded-full" style="background-color: {club1.primary_color}"></span>
								<h3 class="text-base font-bold text-white">{t1.team_name}</h3>
							</div>
							<span class="text-xs font-mono text-gray-400">{t1.matches_played} matches</span>
						</div>
						<div class="text-4xl font-black font-mono text-white">
							{t1.metric_value} <span class="text-lg text-amber-400">{t1.unit}</span>
						</div>
						<!-- Proportional Bar -->
						<div class="w-full bg-[#0a0c10] h-3 rounded overflow-hidden">
							<div
								class="h-full transition-all duration-500"
								style="width: {(Math.abs(t1.metric_value) / maxMetricVal) * 100}%; background-color: {club1.primary_color};"
							></div>
						</div>
					</div>

					<!-- Team 2 Card -->
					<div class="p-6 rounded-lg border border-[#1e2430] bg-[#12161f] space-y-4">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-2">
								<span class="w-3 h-3 rounded-full" style="background-color: {club2.primary_color}"></span>
								<h3 class="text-base font-bold text-white">{t2.team_name}</h3>
							</div>
							<span class="text-xs font-mono text-gray-400">{t2.matches_played} matches</span>
						</div>
						<div class="text-4xl font-black font-mono text-white">
							{t2.metric_value} <span class="text-lg text-amber-400">{t2.unit}</span>
						</div>
						<!-- Proportional Bar -->
						<div class="w-full bg-[#0a0c10] h-3 rounded overflow-hidden">
							<div
								class="h-full transition-all duration-500"
								style="width: {(Math.abs(t2.metric_value) / maxMetricVal) * 100}%; background-color: {club2.primary_color};"
							></div>
						</div>
					</div>
				</div>

				<!-- Comparison Breakdown Table -->
				<div class="overflow-x-auto rounded-lg border border-[#1e2430] bg-[#12161f]">
					<table class="w-full text-xs text-left">
						<thead class="bg-[#0a0c10] text-gray-400 uppercase font-mono border-b border-[#1e2430]">
							<tr>
								<th class="py-3 px-4">Statistical Metric</th>
								<th class="py-3 px-4 font-bold text-white">{t1.team_name}</th>
								<th class="py-3 px-4 font-bold text-white">{t2.team_name}</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-[#1e2430] text-gray-300 font-mono">
							<tr>
								<td class="py-2.5 px-4 font-sans text-gray-400">Wins / Draws / Losses</td>
								<td class="py-2.5 px-4">{t1.wins}W / {t1.draws}D / {t1.losses}L</td>
								<td class="py-2.5 px-4">{t2.wins}W / {t2.draws}D / {t2.losses}L</td>
							</tr>
							<tr>
								<td class="py-2.5 px-4 font-sans text-gray-400">Goals For / Goals Against</td>
								<td class="py-2.5 px-4">{t1.goals_for} GF / {t1.goals_against} GA</td>
								<td class="py-2.5 px-4">{t2.goals_for} GF / {t2.goals_against} GA</td>
							</tr>
							<tr>
								<td class="py-2.5 px-4 font-sans text-gray-400">Goal Difference</td>
								<td class="py-2.5 px-4 font-bold {t1.goal_difference >= 0 ? 'text-emerald-400' : 'text-red-400'}">
									{t1.goal_difference > 0 ? `+${t1.goal_difference}` : t1.goal_difference}
								</td>
								<td class="py-2.5 px-4 font-bold {t2.goal_difference >= 0 ? 'text-emerald-400' : 'text-red-400'}">
									{t2.goal_difference > 0 ? `+${t2.goal_difference}` : t2.goal_difference}
								</td>
							</tr>
							<tr>
								<td class="py-2.5 px-4 font-sans text-gray-400">Clean Sheets</td>
								<td class="py-2.5 px-4">{t1.clean_sheets || 0}</td>
								<td class="py-2.5 px-4">{t2.clean_sheets || 0}</td>
							</tr>
							<tr>
								<td class="py-2.5 px-4 font-sans text-gray-400 font-bold">Selected Metric ({getMetricLabel(metric)})</td>
								<td class="py-2.5 px-4 font-bold text-amber-400">{t1.metric_value} {t1.unit}</td>
								<td class="py-2.5 px-4 font-bold text-amber-400">{t2.metric_value} {t2.unit}</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	{:else}
		<div class="p-12 text-center border border-[#1e2430] rounded-lg bg-[#12161f] text-gray-400">
			No completed matches found matching the specified parameters.
		</div>
	{/if}

	<!-- Saved Insights Shelf -->
	<div class="border-t border-[#1e2430] pt-8 space-y-4">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="text-lg font-bold text-white uppercase tracking-tight">Recent Shareable Insights</h2>
				<p class="text-xs text-gray-400">Reproducible analysis snapshots created by supporters.</p>
			</div>
		</div>

		{#if insights.length === 0}
			<p class="text-xs text-gray-500 py-4">No community insights saved yet. Be the first to publish one above!</p>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each insights as ins}
					<div class="p-4 rounded-lg border border-[#1e2430] bg-[#12161f] hover:border-gray-700 transition flex flex-col justify-between space-y-3">
						<div>
							<div class="flex items-center justify-between gap-2 mb-2">
								<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold uppercase">
									{getMetricLabel(ins.metric)}
								</span>
								<span class="text-[10px] text-gray-500 font-mono">
									{new Date(ins.created_at).toLocaleDateString()}
								</span>
							</div>
							<h3 class="text-sm font-bold text-white leading-snug">{ins.title}</h3>
							{#if ins.description}
								<p class="text-xs text-gray-400 mt-1 line-clamp-2">{ins.description}</p>
							{/if}
						</div>

						<div class="pt-3 border-t border-[#1e2430] flex items-center justify-between">
							<span class="text-[11px] text-gray-400">By <strong>{ins.author_name}</strong></span>
							<button
								type="button"
								onclick={() => loadExistingInsight(ins)}
								class="text-xs font-semibold px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-white border border-[#1e2430] transition"
							>
								Open in Data Lab
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Create Insight Modal -->
	{#if isModalOpen}
		<div class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
			<div class="bg-[#12161f] border border-[#1e2430] rounded-xl max-w-lg w-full p-6 space-y-4">
				<div class="flex items-center justify-between border-b border-[#1e2430] pb-3">
					<h3 class="text-base font-bold text-white">Publish Shareable Insight</h3>
					<button
						type="button"
						onclick={() => (isModalOpen = false)}
						class="text-gray-400 hover:text-white text-sm"
					>
						✕
					</button>
				</div>

				<div class="space-y-3 text-xs">
					<div>
						<label for="ins-title" class="block font-bold text-gray-300 mb-1">Insight Title</label>
						<input
							id="ins-title"
							type="text"
							bind:value={insightTitle}
							class="w-full bg-[#0a0c10] border border-[#1e2430] rounded p-2 text-white focus:outline-none focus:border-gray-500"
						/>
					</div>

					<div>
						<label for="ins-desc" class="block font-bold text-gray-300 mb-1">Notes / Description (Optional)</label>
						<textarea
							id="ins-desc"
							rows="3"
							bind:value={insightDesc}
							class="w-full bg-[#0a0c10] border border-[#1e2430] rounded p-2 text-white focus:outline-none focus:border-gray-500"
						></textarea>
					</div>

					<div class="p-3 rounded bg-[#0a0c10] border border-[#1e2430] text-[11px] text-gray-400 space-y-1">
						<p><strong>Metric:</strong> {getMetricLabel(metric)}</p>
						<p><strong>Venue Filter:</strong> {venue}</p>
						<p class="text-gray-500">
							This insight will store the exact parameters and current statistical snapshot as an immutable object.
						</p>
					</div>
				</div>

				<div class="flex items-center justify-end gap-2 pt-2">
					<button
						type="button"
						onclick={() => (isModalOpen = false)}
						class="px-3 py-1.5 rounded text-xs text-gray-400 hover:text-white"
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={submitInsight}
						disabled={isSavingInsight || !insightTitle}
						class="px-4 py-1.5 rounded text-xs font-bold bg-red-600 hover:bg-red-500 text-white disabled:opacity-50"
					>
						{isSavingInsight ? 'Publishing...' : 'Publish Insight'}
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>
