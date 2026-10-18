<script lang="ts">
	import { onMount } from 'svelte';
	import { queryAnalytics } from '$lib/api/football';
	import type { AnalyticsResponse } from '$lib/types/football';

	let metric = $state('win_rate');
	let team = $state('arsenal');
	let venue = $state('all');
	let loading = $state(false);
	let result = $state<AnalyticsResponse | null>(null);

	async function runQuery() {
		loading = true;
		result = await queryAnalytics({
			metric,
			team_ids: [team],
			venue
		});
		loading = false;
	}

	onMount(() => {
		runQuery();
	});
</script>

<svelte:head>
	<title>Data Lab | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-6 py-12">
	<!-- Header -->
	<div class="mb-8">
		<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-3 bg-amber-500/10 text-amber-400 border border-amber-500/20">
			<span>Explore & Understand</span>
		</div>
		<h1 class="text-3xl font-black text-white">The Data Lab</h1>
		<p class="text-sm text-gray-400 mt-1">
			Query normalized completed football records with explainable formulas and reproducible insights.
		</p>
	</div>

	<!-- Controls & Query Builder -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4 p-6 rounded-xl border border-[#1e2430] bg-[#12161f] mb-8">
		<div>
			<label for="team-select" class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Team</label>
			<select
				id="team-select"
				bind:value={team}
				class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500 transition"
			>
				<option value="arsenal">Arsenal FC</option>
				<option value="real-madrid">Real Madrid CF</option>
				<option value="barcelona">FC Barcelona</option>
				<option value="milan">AC Milan</option>
			</select>
		</div>

		<div>
			<label for="metric-select" class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Metric</label>
			<select
				id="metric-select"
				bind:value={metric}
				class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500 transition"
			>
				<option value="win_rate">Win Rate (%)</option>
				<option value="goals_per_match">Goals Per Match</option>
				<option value="points_per_game">Points Per Game (PPG)</option>
				<option value="goal_difference">Goal Difference</option>
			</select>
		</div>

		<div>
			<label for="venue-select" class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Venue Filter</label>
			<select
				id="venue-select"
				bind:value={venue}
				class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500 transition"
			>
				<option value="all">All Venues</option>
				<option value="home">Home Matches Only</option>
				<option value="away">Away Matches Only</option>
			</select>
		</div>

		<div class="flex items-end">
			<button
				type="button"
				onclick={runQuery}
				disabled={loading}
				class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-semibold text-sm rounded-lg transition shadow-md disabled:opacity-50"
			>
				{loading ? 'Computing...' : 'Calculate Analytics'}
			</button>
		</div>
	</div>

	<!-- Output Display -->
	{#if result && result.series.length > 0}
		{@const s = result.series[0]}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Visual Stat Card -->
			<div class="p-8 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
				<div>
					<span class="text-xs uppercase font-mono tracking-wider text-gray-400">{s.team_name}</span>
					<div class="text-5xl font-black text-white mt-3 mb-1">
						{s.metric_value} <span class="text-2xl text-amber-400 font-normal">{s.unit}</span>
					</div>
					<p class="text-xs text-gray-500 font-mono mt-2">Formula: {result.formula}</p>
				</div>

				<div class="mt-8 pt-4 border-t border-[#1e2430] flex items-center justify-between text-xs text-gray-400">
					<span>Sample Size: <strong>{s.matches_played} matches</strong></span>
					<span class="text-green-400">{s.wins}W</span>
					<span class="text-gray-400">{s.draws}D</span>
					<span class="text-red-400">{s.losses}L</span>
				</div>
			</div>

			<!-- Breakdown -->
			<div class="lg:col-span-2 p-8 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
				<div>
					<h3 class="font-bold text-white text-lg mb-4">Statistical Breakdown</h3>
					<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-[#1e2430]">
							<span class="text-xs text-gray-500">Goals For</span>
							<div class="text-xl font-bold text-white mt-1">{s.goals_for}</div>
						</div>
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-[#1e2430]">
							<span class="text-xs text-gray-500">Goals Against</span>
							<div class="text-xl font-bold text-white mt-1">{s.goals_against}</div>
						</div>
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-[#1e2430]">
							<span class="text-xs text-gray-500">Goal Diff</span>
							<div class="text-xl font-bold {s.goal_difference >= 0 ? 'text-green-400' : 'text-red-400'} mt-1">
								{s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference}
							</div>
						</div>
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-[#1e2430]">
							<span class="text-xs text-gray-500">Venue Mode</span>
							<div class="text-xl font-bold text-amber-400 capitalize mt-1">{result.venue_filter}</div>
						</div>
					</div>
				</div>

				<div class="mt-8 pt-4 border-t border-[#1e2430] text-[11px] text-gray-500 flex items-center justify-between">
					<span>{result.disclaimer}</span>
					<span>Verified Canonical Computation</span>
				</div>
			</div>
		</div>
	{:else}
		<div class="p-12 text-center border border-[#1e2430] rounded-xl bg-[#12161f] text-gray-400">
			{#if loading}
				<p>Calculating verified analytics metrics...</p>
			{:else}
				<p>No matches found matching the specified parameters. Select an eligible season or venue.</p>
			{/if}
		</div>
	{/if}
</div>
