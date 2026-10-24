<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { fetchSquad, comparePlayers } from '$lib/api/football';
	import type { Player, PlayerComparison } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedClubId = $state('arsenal');
	let selectedPosition = $state('all');
	let players = $state<Player[]>([]);
	let isLoading = $state(false);

	// Player comparison state
	let comparePlayer1Id = $state<string | null>(null);
	let comparePlayer2Id = $state<string | null>(null);
	let comparisonResult = $state<PlayerComparison | null>(null);
	let isComparing = $state(false);

	let isInitialized = false;
	const viewingClub = $derived(themeState.currentTheme);
	const clubList = Object.values(CLUBS);

	$effect(() => {
		if (!isInitialized && data.players) {
			players = data.players;
			selectedClubId = data.activeClubId || viewingClub.id;
			if (data.initialCompare1 && data.initialCompare2) {
				comparePlayer1Id = data.initialCompare1;
				comparePlayer2Id = data.initialCompare2;
				runComparison(data.initialCompare1, data.initialCompare2);
			}
			isInitialized = true;
		}
	});

	async function loadSquad(clubId: string, pos?: string) {
		isLoading = true;
		try {
			const posFilter = pos && pos !== 'all' ? pos : undefined;
			const res = await fetchSquad(clubId, posFilter);
			players = res;
		} finally {
			isLoading = false;
		}
	}

	function handleClubChange(clubId: string) {
		selectedClubId = clubId;
		loadSquad(clubId, selectedPosition);
	}

	function handlePositionChange(pos: string) {
		selectedPosition = pos;
		loadSquad(selectedClubId, pos);
	}

	async function runComparison(p1Id: string, p2Id: string) {
		isComparing = true;
		try {
			const res = await comparePlayers(p1Id, p2Id);
			comparisonResult = res;
		} finally {
			isComparing = false;
		}
	}

	function toggleCompare(playerId: string) {
		if (comparePlayer1Id === playerId) {
			comparePlayer1Id = null;
			comparisonResult = null;
		} else if (comparePlayer2Id === playerId) {
			comparePlayer2Id = null;
			comparisonResult = null;
		} else if (!comparePlayer1Id) {
			comparePlayer1Id = playerId;
		} else if (!comparePlayer2Id) {
			comparePlayer2Id = playerId;
			runComparison(comparePlayer1Id, playerId);
		} else {
			// Replace player 2
			comparePlayer2Id = playerId;
			runComparison(comparePlayer1Id, playerId);
		}
	}
</script>

<svelte:head>
	<title>Squad Explorer & Player Comparisons | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
	<!-- Page Header -->
	<div class="border-b border-[#1e2430] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
				Tactical Roster & Metrics
			</div>
			<h1 class="text-2xl sm:text-3xl font-black text-white uppercase tracking-tight">Squad Explorer</h1>
			<p class="text-xs sm:text-sm text-gray-400 mt-1">
				Examine individual player contributions, discipline, and compare rivals head-to-head.
			</p>
		</div>

		{#if comparePlayer1Id || comparePlayer2Id}
			<div class="flex items-center gap-2 bg-[#0d1017] p-2 rounded-lg border border-[#1e2430] text-xs">
				<span class="text-gray-400 font-mono text-[11px]">Compare ({comparePlayer1Id ? 1 : 0} + {comparePlayer2Id ? 1 : 0}/2):</span>
				<button
					type="button"
					onclick={() => {
						comparePlayer1Id = null;
						comparePlayer2Id = null;
						comparisonResult = null;
					}}
					class="text-amber-400 hover:text-white font-semibold transition"
				>
					Clear Selection
				</button>
			</div>
		{/if}
	</div>

	<!-- Active Comparison Panel -->
	{#if comparisonResult}
		{@const p1 = comparisonResult.player1.player}
		{@const p2 = comparisonResult.player2.player}
		{@const club1 = CLUBS[p1.club_id] || CLUBS.arsenal}
		{@const club2 = CLUBS[p2.club_id] || CLUBS.arsenal}
		<section class="p-6 rounded-xl border border-amber-500/40 bg-gradient-to-br from-[#161c28] via-[#12161f] to-[#0d1017] shadow-xl space-y-6">
			<div class="flex items-center justify-between border-b border-[#1e2430] pb-4">
				<div class="flex items-center gap-2">
					<span class="text-amber-400 font-bold text-sm uppercase tracking-wider font-mono">⚡ Head-to-Head Comparison</span>
				</div>
				<button
					type="button"
					onclick={() => (comparisonResult = null)}
					class="text-gray-400 hover:text-white text-xs font-mono"
				>
					Close ✕
				</button>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
				<!-- Player 1 Profile Card -->
				<div class="p-4 rounded-xl border border-[#1e2430] bg-[#0d1017]/80 flex items-center gap-4">
					<span class="w-12 h-12 rounded-full flex items-center justify-center font-black text-xl text-white shadow" style="background-color: {club1.primary_color}">
						#{p1.jersey_number}
					</span>
					<div>
						<div class="flex items-center gap-2">
							<h3 class="text-base font-bold text-white">{p1.name}</h3>
							<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-gray-400 border border-[#1e2430]">
								{club1.short_name}
							</span>
						</div>
						<p class="text-xs text-gray-400">{p1.position} • {p1.nationality}</p>
					</div>
				</div>

				<!-- Player 2 Profile Card -->
				<div class="p-4 rounded-xl border border-[#1e2430] bg-[#0d1017]/80 flex items-center gap-4">
					<span class="w-12 h-12 rounded-full flex items-center justify-center font-black text-xl text-white shadow" style="background-color: {club2.primary_color}">
						#{p2.jersey_number}
					</span>
					<div>
						<div class="flex items-center gap-2">
							<h3 class="text-base font-bold text-white">{p2.name}</h3>
							<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-gray-400 border border-[#1e2430]">
								{club2.short_name}
							</span>
						</div>
						<p class="text-xs text-gray-400">{p2.position} • {p2.nationality}</p>
					</div>
				</div>
			</div>

			<!-- Comparison Metrics Comparison Matrix -->
			<div class="space-y-3 pt-2">
				<div class="grid grid-cols-3 gap-2 text-center text-xs font-mono border-b border-[#1e2430] pb-2 text-gray-400">
					<span class="font-bold text-white">{p1.short_name}</span>
					<span class="uppercase font-semibold text-amber-400">Metric</span>
					<span class="font-bold text-white">{p2.short_name}</span>
				</div>

				<!-- Goals -->
				<div class="grid grid-cols-3 gap-2 text-center text-xs py-1.5 border-b border-[#1e2430]/60 items-center">
					<span class="font-bold text-white text-sm">{p1.goals}</span>
					<span class="text-gray-400">Total Goals</span>
					<span class="font-bold text-white text-sm">{p2.goals}</span>
				</div>

				<!-- Assists -->
				<div class="grid grid-cols-3 gap-2 text-center text-xs py-1.5 border-b border-[#1e2430]/60 items-center">
					<span class="font-bold text-white text-sm">{p1.assists}</span>
					<span class="text-gray-400">Total Assists</span>
					<span class="font-bold text-white text-sm">{p2.assists}</span>
				</div>

				<!-- Goals per 90 -->
				<div class="grid grid-cols-3 gap-2 text-center text-xs py-1.5 border-b border-[#1e2430]/60 items-center">
					<span class="font-bold text-emerald-400 font-mono">{comparisonResult.player1.goals_per_90}</span>
					<span class="text-gray-400">Goals / 90 min</span>
					<span class="font-bold text-emerald-400 font-mono">{comparisonResult.player2.goals_per_90}</span>
				</div>

				<!-- Mins per Goal Contribution -->
				<div class="grid grid-cols-3 gap-2 text-center text-xs py-1.5 border-b border-[#1e2430]/60 items-center">
					<span class="font-bold text-amber-400 font-mono">{comparisonResult.player1.minutes_per_contribution}m</span>
					<span class="text-gray-400">Mins / G+A Contribution</span>
					<span class="font-bold text-amber-400 font-mono">{comparisonResult.player2.minutes_per_contribution}m</span>
				</div>

				<!-- Discipline -->
				<div class="grid grid-cols-3 gap-2 text-center text-xs py-1.5 items-center">
					<span class="font-bold text-purple-400 font-mono">{comparisonResult.player1.discipline_score} / 10</span>
					<span class="text-gray-400">Fairplay Rating</span>
					<span class="font-bold text-purple-400 font-mono">{comparisonResult.player2.discipline_score} / 10</span>
				</div>
			</div>

			<!-- Analysis Summary Banner -->
			<div class="p-3.5 rounded-lg bg-[#0d1017] border border-[#1e2430] text-xs text-amber-200/90 font-mono">
				💡 <strong>Tactical Verdict:</strong> {comparisonResult.comparison_summary}
			</div>
		</section>
	{/if}

	<!-- Club and Position Filter Tabs -->
	<div class="space-y-4">
		<!-- Club Selector -->
		<div class="flex flex-wrap items-center gap-2">
			<span class="text-xs uppercase font-bold text-gray-500 mr-2">Club:</span>
			{#each clubList as club}
				{@const isSelected = selectedClubId === club.id}
				<button
					type="button"
					onclick={() => handleClubChange(club.id)}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 border {isSelected ? 'bg-white/10 text-white border-white/30' : 'bg-[#12161f] text-gray-400 border-[#1e2430] hover:text-white'}"
				>
					<span class="w-2.5 h-2.5 rounded-full" style="background-color: {club.primary_color}"></span>
					<span>{club.name}</span>
				</button>
			{/each}
		</div>

		<!-- Position Selector -->
		<div class="flex flex-wrap items-center gap-2">
			<span class="text-xs uppercase font-bold text-gray-500 mr-2">Position:</span>
			{#each ['all', 'Goalkeeper', 'Defender', 'Midfielder', 'Attacker'] as pos}
				{@const isSelected = selectedPosition === pos}
				<button
					type="button"
					onclick={() => handlePositionChange(pos)}
					class="px-3 py-1 rounded text-xs font-semibold transition border {isSelected ? 'bg-red-600 text-white border-red-500' : 'bg-[#0d1017] text-gray-400 border-[#1e2430] hover:text-white'}"
				>
					{pos === 'all' ? 'All Positions' : pos}
				</button>
			{/each}
		</div>
	</div>

	<!-- Players Grid -->
	{#if isLoading}
		<div class="py-16 text-center text-gray-500 text-sm">
			Loading squad profiles...
		</div>
	{:else if players.length === 0}
		<div class="py-16 text-center border border-dashed border-[#1e2430] rounded-xl text-gray-500 text-sm">
			No players found for the selected filters.
		</div>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
			{#each players as player}
				{@const club = CLUBS[player.club_id] || CLUBS.arsenal}
				{@const isSelectedP1 = comparePlayer1Id === player.id}
				{@const isSelectedP2 = comparePlayer2Id === player.id}
				<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between space-y-4 hover:border-gray-600 transition">
					<!-- Top Row: Jersey + Name + Position -->
					<div>
						<div class="flex items-center justify-between mb-3">
							<span class="text-xs font-black font-mono px-2 py-0.5 rounded bg-black/50 text-white border border-[#1e2430]">
								#{player.jersey_number}
							</span>
							<span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/5 text-gray-300 border border-[#1e2430]">
								{player.position}
							</span>
						</div>

						<h3 class="text-base font-bold text-white">{player.name}</h3>
						<p class="text-xs text-gray-400 font-mono mt-0.5">
							{club.short_name} • {player.nationality}
						</p>
					</div>

					<!-- Stats Grid -->
					<div class="grid grid-cols-3 gap-2 bg-[#0d1017] p-2.5 rounded-lg border border-[#1e2430] text-center text-xs">
						<div>
							<p class="text-[10px] text-gray-500 uppercase">Apps</p>
							<p class="font-bold text-white font-mono">{player.appearances}</p>
						</div>
						<div>
							<p class="text-[10px] text-gray-500 uppercase">Goals</p>
							<p class="font-bold text-emerald-400 font-mono">{player.goals}</p>
						</div>
						<div>
							<p class="text-[10px] text-gray-500 uppercase">Assists</p>
							<p class="font-bold text-amber-400 font-mono">{player.assists}</p>
						</div>
					</div>

					<!-- Footer & Compare Action -->
					<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-xs">
						<span class="text-[11px] text-gray-500 font-mono">
							G+A: {player.goal_contributions}
						</span>
						<button
							type="button"
							onclick={() => toggleCompare(player.id)}
							class="px-2.5 py-1 rounded text-xs font-semibold transition border {isSelectedP1 || isSelectedP2 ? 'bg-amber-400 text-black border-amber-400 font-bold' : 'bg-white/5 text-gray-300 border-[#1e2430] hover:text-white hover:bg-white/10'}"
						>
							{isSelectedP1 || isSelectedP2 ? 'Selected ✓' : '+ Compare'}
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
