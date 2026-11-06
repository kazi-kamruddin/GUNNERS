<script lang="ts">
	import { fetchSquad, comparePlayers } from '$lib/api/football';
	import type { Player, PlayerComparison } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedPosition = $state('all');
	let players = $state<Player[]>([]);
	let isLoading = $state(false);

	// Player comparison state
	let comparePlayer1Id = $state<string | null>(null);
	let comparePlayer2Id = $state<string | null>(null);
	let comparisonResult = $state<PlayerComparison | null>(null);
	let isComparing = $state(false);

	let isInitialized = false;

	$effect(() => {
		if (!isInitialized && data.players) {
			players = data.players;
			if (data.initialCompare1 && data.initialCompare2) {
				comparePlayer1Id = data.initialCompare1;
				comparePlayer2Id = data.initialCompare2;
				runComparison(data.initialCompare1, data.initialCompare2);
			}
			isInitialized = true;
		}
	});

	async function loadSquad(pos?: string) {
		isLoading = true;
		try {
			const posFilter = pos && pos !== 'all' ? pos : undefined;
			const res = await fetchSquad('arsenal', posFilter);
			players = res;
		} finally {
			isLoading = false;
		}
	}

	function handlePositionChange(pos: string) {
		selectedPosition = pos;
		loadSquad(pos);
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
	<title>Arsenal 2024/25 Squad & Player Comparisons | GUNNERS</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
	<!-- Page Header -->
	<div class="border-b border-red-900/30 pb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-red-950/70 text-red-400 border border-red-800/40 font-mono">
				Mikel Arteta's 2024/25 First Team
			</div>
			<h1 class="text-3xl font-black text-white uppercase tracking-tight flex items-center gap-2.5">
				<span>Arsenal Squad Directory</span>
			</h1>
			<p class="text-sm text-gray-400 mt-1 max-w-2xl">
				Official roster statistics, goal contributions, appearances, discipline ratings, and head-to-head tactical comparisons.
			</p>
		</div>

		<div class="flex items-center gap-2">
			<a
				href="/board"
				class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition shadow-sm flex items-center gap-1.5"
			>
				<span>📋</span>
				<span>Build Lineup in Dugout</span>
			</a>
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
						Clear ✕
					</button>
				</div>
			{/if}
		</div>
	</div>

	<!-- Active Comparison Panel -->
	{#if comparisonResult}
		{@const p1 = comparisonResult.player1.player}
		{@const p2 = comparisonResult.player2.player}
		<section class="p-6 rounded-2xl border border-amber-500/40 bg-gradient-to-br from-[#161c28] via-[#12161f] to-[#0d1017] shadow-xl space-y-6">
			<div class="flex items-center justify-between border-b border-[#1e2430] pb-4">
				<div class="flex items-center gap-2">
					<span class="text-amber-400 font-bold text-sm uppercase tracking-wider font-mono">⚡ Gunner Head-to-Head Comparison</span>
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
				<div class="p-4 rounded-xl border border-red-900/40 bg-[#0d1017]/80 flex items-center gap-4">
					<span class="w-12 h-12 rounded-full flex items-center justify-center font-black text-xl text-white shadow bg-red-600">
						#{p1.jersey_number}
					</span>
					<div>
						<div class="flex items-center gap-2">
							<h3 class="text-base font-bold text-white">{p1.name}</h3>
							<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950/60 text-red-300 border border-red-900/40">
								Arsenal
							</span>
						</div>
						<p class="text-xs text-gray-400">{p1.position} • {p1.nationality}</p>
					</div>
				</div>

				<!-- Player 2 Profile Card -->
				<div class="p-4 rounded-xl border border-red-900/40 bg-[#0d1017]/80 flex items-center gap-4">
					<span class="w-12 h-12 rounded-full flex items-center justify-center font-black text-xl text-white shadow bg-red-600">
						#{p2.jersey_number}
					</span>
					<div>
						<div class="flex items-center gap-2">
							<h3 class="text-base font-bold text-white">{p2.name}</h3>
							<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950/60 text-red-300 border border-red-900/40">
								Arsenal
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

	<!-- Position Filter Tabs -->
	<div class="flex items-center gap-2 border-b border-[#1e2430] pb-4 flex-wrap">
		{#each ['all', 'Goalkeeper', 'Defender', 'Midfielder', 'Attacker'] as pos}
			{@const isSelected = selectedPosition === pos}
			<button
				type="button"
				onclick={() => handlePositionChange(pos)}
				class="px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 border {isSelected ? 'bg-red-600 text-white border-red-500 shadow-sm' : 'bg-[#12161f] text-gray-400 border-[#1e2430] hover:text-white'}"
			>
				<span>{pos === 'all' ? 'All Gunners' : pos + 's'}</span>
			</button>
		{/each}
	</div>

	<!-- Players Grid -->
	{#if isLoading}
		<div class="py-16 text-center text-gray-500 text-sm">
			Loading Arsenal squad profiles...
		</div>
	{:else if players.length === 0}
		<div class="py-16 text-center border border-dashed border-[#1e2430] rounded-xl text-gray-500 text-sm">
			No players found for the selected position.
		</div>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
			{#each players as player}
				{@const isSelectedP1 = comparePlayer1Id === player.id}
				{@const isSelectedP2 = comparePlayer2Id === player.id}
				<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between space-y-4 hover:border-red-900/60 transition group">
					<!-- Top Row: Jersey + Name + Position -->
					<div>
						<div class="flex items-center justify-between mb-3">
							<span class="text-xs font-black font-mono px-2 py-0.5 rounded bg-red-950/80 text-red-300 border border-red-800/40">
								#{player.jersey_number}
							</span>
							<span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/5 text-gray-300 border border-[#1e2430]">
								{player.position}
							</span>
						</div>

						<h3 class="text-base font-bold text-white group-hover:text-red-400 transition">{player.name}</h3>
						<p class="text-xs text-gray-400 font-mono mt-0.5">
							Arsenal FC • {player.nationality}
						</p>
					</div>

					<!-- Stats Grid -->
					<div class="grid grid-cols-3 gap-2 bg-[#0a0c10] p-2.5 rounded-lg border border-[#1e2430] text-center text-xs">
						<div>
							<p class="text-[10px] text-gray-500 uppercase">Apps</p>
							<p class="font-bold text-white font-mono">{player.appearances}</p>
						</div>
						<div>
							<p class="text-[10px] text-gray-500 uppercase">{player.position === 'Goalkeeper' ? 'Cleans' : 'Goals'}</p>
							<p class="font-bold text-emerald-400 font-mono">{player.position === 'Goalkeeper' ? player.clean_sheets : player.goals}</p>
						</div>
						<div>
							<p class="text-[10px] text-gray-500 uppercase">{player.position === 'Goalkeeper' ? 'Mins' : 'Assists'}</p>
							<p class="font-bold text-amber-400 font-mono">{player.position === 'Goalkeeper' ? player.minutes_played : player.assists}</p>
						</div>
					</div>

					<!-- Footer & Actions -->
					<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-xs gap-2">
						<a
							href="/board"
							class="text-[11px] text-red-400 hover:text-red-300 font-semibold flex items-center gap-1 transition"
						>
							<span>📋</span>
							<span>Lineup</span>
						</a>
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
