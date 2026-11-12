<script lang="ts">
	import { fetchSquad, comparePlayers } from '$lib/api/football';
	import type { Player, PlayerComparison } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedPosition = $state('all');
	let players = $state<Player[]>([]);
	let isLoading = $state(false);

	let comparePlayer1Id = $state<string | null>(null);
	let comparePlayer2Id = $state<string | null>(null);
	let comparisonResult = $state<PlayerComparison | null>(null);
	let isComparing = $state(false);
	let failedPortraits = $state<Record<string, boolean>>({});
	let failedActions = $state<Record<string, boolean>>({});

	function getInitials(name: string): string {
		return name
			.split(/\s+/)
			.map((p) => p[0] || '')
			.join('')
			.slice(0, 2)
			.toUpperCase();
	}

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
			comparePlayer2Id = playerId;
			runComparison(comparePlayer1Id, playerId);
		}
	}
</script>

<svelte:head>
	<title>Arsenal 2024/25 Squad & Player Comparisons | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-10">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
		<div class="space-y-3">
			<h1>Arsenal squad directory</h1>
			<p class="lead text-ink-2">
				Mikel Arteta’s first-team roster statistics, appearances, goal contributions, and head-to-head player comparisons.
			</p>
		</div>

		<div class="flex items-center gap-3 flex-wrap">
			<a
				href="/board"
				class="inline-flex items-center h-10 px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 font-semibold text-sm transition-opacity whitespace-nowrap"
			>
				Build lineup in Dugout
			</a>
			{#if comparePlayer1Id || comparePlayer2Id}
				<div class="flex items-center gap-3 bg-paper-2 px-3 h-10 rounded-card border border-rule text-xs">
					<span class="num text-muted">Selected ({comparePlayer1Id ? 1 : 0} + {comparePlayer2Id ? 1 : 0}/2)</span>
					<button
						type="button"
						onclick={() => {
							comparePlayer1Id = null;
							comparePlayer2Id = null;
							comparisonResult = null;
						}}
						class="text-accent-2 hover:text-ink font-semibold transition-colors whitespace-nowrap"
					>
						Clear selection
					</button>
				</div>
			{/if}
		</div>
	</div>

	<!-- Active Comparison Panel -->
	{#if comparisonResult}
		{@const p1 = comparisonResult.player1.player}
		{@const p2 = comparisonResult.player2.player}
		<section class="bg-paper-2 border-t-2 border-rule-2 p-6 space-y-6">
			<div class="flex items-center justify-between border-b border-rule pb-4">
				<h2>Head-to-head player comparison</h2>
				<button
					type="button"
					onclick={() => (comparisonResult = null)}
					class="text-muted hover:text-ink text-sm font-semibold transition-colors whitespace-nowrap"
				>
					Close comparison
				</button>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
				<div class="border-t border-rule pt-4 flex items-center gap-4">
					<span class="num font-display font-bold text-2xl text-accent">
						#{p1.jersey_number}
					</span>
					<div>
						<h3 class="text-base font-bold text-ink">{p1.name}</h3>
						<p class="text-xs text-muted">{p1.position}, {p1.nationality}</p>
					</div>
				</div>

				<div class="border-t border-rule pt-4 flex items-center gap-4">
					<span class="num font-display font-bold text-2xl text-accent">
						#{p2.jersey_number}
					</span>
					<div>
						<h3 class="text-base font-bold text-ink">{p2.name}</h3>
						<p class="text-xs text-muted">{p2.position}, {p2.nationality}</p>
					</div>
				</div>
			</div>

			<!-- Comparison Metrics Table -->
			<div class="divide-y divide-rule border-y border-rule text-sm">
				<div class="grid grid-cols-3 gap-4 py-2.5 text-xs text-muted font-semibold">
					<span>{p1.short_name}</span>
					<span class="text-center">Metric</span>
					<span class="text-right">{p2.short_name}</span>
				</div>

				<div class="grid grid-cols-3 gap-4 py-2.5 items-center">
					<span class="num font-semibold text-ink">{p1.goals}</span>
					<span class="text-center text-xs text-muted">Total goals</span>
					<span class="num font-semibold text-ink text-right">{p2.goals}</span>
				</div>

				<div class="grid grid-cols-3 gap-4 py-2.5 items-center">
					<span class="num font-semibold text-ink">{p1.assists}</span>
					<span class="text-center text-xs text-muted">Total assists</span>
					<span class="num font-semibold text-ink text-right">{p2.assists}</span>
				</div>

				<div class="grid grid-cols-3 gap-4 py-2.5 items-center">
					<span class="num font-outlier font-semibold text-success">{comparisonResult.player1.goals_per_90}</span>
					<span class="text-center text-xs text-muted">Goals per 90 min</span>
					<span class="num font-outlier font-semibold text-success text-right">{comparisonResult.player2.goals_per_90}</span>
				</div>

				<div class="grid grid-cols-3 gap-4 py-2.5 items-center">
					<span class="num font-outlier font-semibold text-accent-2">{comparisonResult.player1.minutes_per_contribution}m</span>
					<span class="text-center text-xs text-muted">Minutes per G+A</span>
					<span class="num font-outlier font-semibold text-accent-2 text-right">{comparisonResult.player2.minutes_per_contribution}m</span>
				</div>

				<div class="grid grid-cols-3 gap-4 py-2.5 items-center">
					<span class="num font-outlier font-semibold text-ink">{comparisonResult.player1.discipline_score} / 10</span>
					<span class="text-center text-xs text-muted">Fairplay rating</span>
					<span class="num font-outlier font-semibold text-ink text-right">{comparisonResult.player2.discipline_score} / 10</span>
				</div>
			</div>

			<p class="text-sm text-ink-2">
				<strong class="text-ink font-semibold">Tactical verdict:</strong> {comparisonResult.comparison_summary}
			</p>
		</section>
	{/if}

	<!-- Position Filter Tabs -->
	<div class="flex items-center gap-2 border-b border-rule pb-4 flex-wrap">
		{#each ['all', 'Goalkeeper', 'Defender', 'Midfielder', 'Attacker'] as pos}
			{@const isSelected = selectedPosition === pos}
			{@const posLabel = pos === 'all' ? 'All Gunners' : pos + 's'}
			<button
				type="button"
				onclick={() => handlePositionChange(pos)}
				class="h-9 px-4 rounded-card text-sm font-semibold transition-colors border whitespace-nowrap {isSelected ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				{posLabel}
			</button>
		{/each}
	</div>

	<!-- Players Grid -->
	{#if isLoading}
		<div class="py-12 text-muted text-sm">
			Loading Arsenal squad profiles…
		</div>
	{:else if players.length === 0}
		<div class="border-t border-rule pt-8 text-muted text-sm">
			No players found for the selected position.
		</div>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
			{#each players as player}
				{@const isSelectedP1 = comparePlayer1Id === player.id}
				{@const isSelectedP2 = comparePlayer2Id === player.id}
				{@const compareBtnLabel = isSelectedP1 || isSelectedP2 ? 'Selected' : 'Compare'}
				{@const portraitSrc = player.portrait_url || player.photo_url}
				{@const actionSrc = player.action_url}
				{@const showPortrait = Boolean(portraitSrc && !failedPortraits[player.id])}
				{@const showAction = Boolean(actionSrc && !failedActions[player.id])}
				<article class="border-t border-rule pt-5 flex flex-col justify-between space-y-5">
					<a href="/squad/{encodeURIComponent(player.id)}" class="group block space-y-4">
						<div class="relative aspect-[4/5] w-full rounded-card overflow-hidden bg-paper-2 border border-rule">
							{#if showPortrait}
								<img
									src={portraitSrc}
									alt="{player.name} portrait"
									width="400"
									height="500"
									loading="lazy"
									class="w-full h-full object-cover object-top transition-opacity duration-300 {showAction ? 'group-hover:opacity-0 group-focus-within:opacity-0' : ''}"
									onerror={() => {
										failedPortraits = { ...failedPortraits, [player.id]: true };
									}}
								/>
								{#if showAction}
									<img
										src={actionSrc}
										alt=""
										aria-hidden="true"
										width="400"
										height="500"
										loading="lazy"
										class="absolute inset-0 w-full h-full object-cover object-top opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-300"
										onerror={() => {
											failedActions = { ...failedActions, [player.id]: true };
										}}
									/>
								{/if}
							{:else if showAction}
								<img
									src={actionSrc}
									alt={player.name}
									width="400"
									height="500"
									loading="lazy"
									class="w-full h-full object-cover object-top"
									onerror={() => {
										failedActions = { ...failedActions, [player.id]: true };
									}}
								/>
							{:else}
								<div class="w-full h-full flex flex-col items-center justify-center gap-2 bg-paper-2 p-4 text-center">
									<span class="num font-display font-bold text-4xl text-accent">#{player.jersey_number}</span>
									<span class="font-display font-bold text-lg text-ink">{getInitials(player.name)}</span>
									<span class="text-xs text-muted">{player.position}</span>
								</div>
							{/if}
						</div>

						<div class="space-y-1.5">
							<div class="flex items-center justify-between text-xs text-muted">
								<span class="num font-outlier font-semibold text-accent">#{player.jersey_number}</span>
								<span>{player.position}</span>
							</div>

							<h3 class="text-base font-bold text-ink group-hover:text-accent transition-colors">{player.name}</h3>
							<p class="text-xs text-muted">
								Arsenal FC, {player.nationality}
							</p>
						</div>
					</a>

					<!-- Stats Row -->
					<div class="grid grid-cols-3 gap-3 border-y border-rule py-3 text-xs">
						<div>
							<div class="text-muted">Apps</div>
							<div class="num font-outlier font-semibold text-sm text-ink">{player.appearances}</div>
						</div>
						<div>
							<div class="text-muted">{player.position === 'Goalkeeper' ? 'Clean sheets' : 'Goals'}</div>
							<div class="num font-outlier font-semibold text-sm text-success">{player.position === 'Goalkeeper' ? player.clean_sheets : player.goals}</div>
						</div>
						<div>
							<div class="text-muted">{player.position === 'Goalkeeper' ? 'Minutes' : 'Assists'}</div>
							<div class="num font-outlier font-semibold text-sm text-accent-2">{player.position === 'Goalkeeper' ? player.minutes_played : player.assists}</div>
						</div>
					</div>

					<!-- Footer & Actions -->
					<div class="flex items-center justify-between text-xs gap-2">
						<a
							href="/squad/{encodeURIComponent(player.id)}"
							class="text-ink-2 hover:text-accent font-semibold transition-colors whitespace-nowrap"
						>
							Player dossier
						</a>
						<button
							type="button"
							onclick={() => toggleCompare(player.id)}
							class="h-8 px-3 rounded-card text-xs font-semibold transition-colors border whitespace-nowrap {isSelectedP1 || isSelectedP2 ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
						>
							{compareBtnLabel}
						</button>
					</div>
				</article>
			{/each}
		</div>
	{/if}
</div>
