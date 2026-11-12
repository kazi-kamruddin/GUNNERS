<script lang="ts">
	import { replaceState } from '$app/navigation';
	import { tick, untrack } from 'svelte';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { ApiError, fetchSquadResult, comparePlayersStrict } from '$lib/api/football';
	import type { Player, PlayerComparison } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedPosition = $state(untrack(() => data.activePosition || 'all'));
	let players = $state<Player[]>(untrack(() => data.players ?? []));
	let squadError = $state<string | null>(untrack(() => data.squadError ?? null));
	let isLoading = $state(false);

	let comparePlayer1Id = $state<string | null>(untrack(() => data.initialCompare1 || null));
	let comparePlayer2Id = $state<string | null>(untrack(() => data.initialCompare2 || null));
	let comparisonResult = $state<PlayerComparison | null>(null);
	let compareError = $state<string | null>(null);
	let isComparing = $state(false);
	let failedPortraits = $state<Record<string, boolean>>({});
	let failedActions = $state<Record<string, boolean>>({});
	let comparisonSectionEl = $state<HTMLElement | null>(null);

	let squadRequestSeq = 0;
	let compareRequestSeq = 0;
	let lastAutoComparedPair = '';

	function getInitials(name: string): string {
		return name
			.split(/\s+/)
			.map((p) => p[0] || '')
			.join('')
			.slice(0, 2)
			.toUpperCase();
	}

	$effect(() => {
		players = data.players ?? [];
		squadError = data.squadError ?? null;
		selectedPosition = data.activePosition || 'all';
		comparePlayer1Id = data.initialCompare1 || null;
		comparePlayer2Id = data.initialCompare2 || null;

		if (data.initialCompare1 && data.initialCompare2) {
			const pairKey = `${data.initialCompare1}|${data.initialCompare2}`;
			if (pairKey !== lastAutoComparedPair) {
				lastAutoComparedPair = pairKey;
				void runComparison(data.initialCompare1, data.initialCompare2, false);
			}
		} else {
			lastAutoComparedPair = '';
			comparisonResult = null;
		}
	});

	$effect(() => {
		if (!comparePlayer1Id || !comparePlayer2Id) {
			compareError = null;
		}
		if (typeof window === 'undefined') return;
		const nextUrl = new URL(window.location.href);
		if (selectedPosition && selectedPosition !== 'all') {
			nextUrl.searchParams.set('position', selectedPosition);
		} else {
			nextUrl.searchParams.delete('position');
		}
		if (comparePlayer1Id) {
			nextUrl.searchParams.set('compare1', comparePlayer1Id);
		} else {
			nextUrl.searchParams.delete('compare1');
		}
		if (comparePlayer2Id) {
			nextUrl.searchParams.set('compare2', comparePlayer2Id);
		} else {
			nextUrl.searchParams.delete('compare2');
		}
		if (nextUrl.search !== window.location.search) {
			replaceState(nextUrl, {});
		}
	});

	async function loadSquad(pos?: string) {
		const seq = ++squadRequestSeq;
		isLoading = true;
		try {
			const posFilter = pos && pos !== 'all' ? pos : undefined;
			const res = await fetchSquadResult('arsenal', posFilter);
			if (seq !== squadRequestSeq) return;
			squadError = res.error;
			if (!res.error) {
				players = res.data;
			}
		} finally {
			if (seq === squadRequestSeq) {
				isLoading = false;
			}
		}
	}

	function handlePositionChange(pos: string) {
		selectedPosition = pos;
		void loadSquad(pos);
	}

	async function runComparison(p1Id: string, p2Id: string, shouldScroll = true) {
		const seq = ++compareRequestSeq;
		isComparing = true;
		compareError = null;
		try {
			const res = await comparePlayersStrict(p1Id, p2Id);
			if (seq !== compareRequestSeq) return;
			comparisonResult = res;
			if (shouldScroll && typeof window !== 'undefined') {
				await tick();
				const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
				comparisonSectionEl?.scrollIntoView({
					behavior: prefersReduced ? 'auto' : 'smooth',
					block: 'start'
				});
				comparisonSectionEl?.focus({ preventScroll: true });
			}
		} catch (err) {
			if (seq !== compareRequestSeq) return;
			comparisonResult = null;
			compareError =
				err instanceof ApiError
					? err.detail
					: 'Unable to compare the selected Arsenal players right now.';
		} finally {
			if (seq === compareRequestSeq) {
				isComparing = false;
			}
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
			if (comparePlayer2Id) {
				void runComparison(playerId, comparePlayer2Id, true);
			}
		} else if (!comparePlayer2Id) {
			comparePlayer2Id = playerId;
			void runComparison(comparePlayer1Id, playerId, true);
		} else {
			comparePlayer2Id = playerId;
			void runComparison(comparePlayer1Id, playerId, true);
		}
	}
</script>

<svelte:head>
	<title>Arsenal First-Team Squad & Player Comparisons | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-10">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
		<div class="space-y-3">
			<h1 class="text-[length:var(--text-display-s)]">Arsenal squad directory</h1>
			<p class="lead text-ink-2">
				Mikel Arteta’s first-team roster statistics, appearances, goal contributions, and head-to-head player comparisons.
			</p>
		</div>

		<div class="flex items-center gap-3 flex-wrap">
			<a
				href="/board"
				class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 font-semibold text-sm transition-opacity whitespace-nowrap"
			>
				Build lineup in Dugout
			</a>
			{#if comparePlayer1Id || comparePlayer2Id}
				<div class="flex items-center gap-3 bg-paper-2 px-3 min-h-[44px] rounded-card border border-rule text-xs">
					<span class="num text-muted">Selected ({(comparePlayer1Id ? 1 : 0) + (comparePlayer2Id ? 1 : 0)}/2)</span>
					<button
						type="button"
						onclick={() => {
							comparePlayer1Id = null;
							comparePlayer2Id = null;
							comparisonResult = null;
						}}
						class="min-h-[44px] px-1 text-accent-2 hover:text-ink font-semibold transition-colors whitespace-nowrap"
					>
						Clear selection
					</button>
				</div>
			{/if}
		</div>
	</div>

	{#if isComparing}
		<div
			role="status"
			aria-live="polite"
			class="bg-paper-2 border-y border-rule border-t-2 border-t-accent-2 p-4 text-sm text-ink-2"
		>
			Comparing selected Arsenal players…
		</div>
	{/if}

	{#if compareError}
		<StateBanner
			variant="error"
			title="Player comparison unavailable"
			message={compareError}
			busy={isComparing}
			onretry={() => {
				if (comparePlayer1Id && comparePlayer2Id) {
					void runComparison(comparePlayer1Id, comparePlayer2Id, false);
				}
			}}
		/>
	{/if}

	<!-- Active Comparison Panel -->
	{#if comparisonResult}
		{@const p1 = comparisonResult.player1.player}
		{@const p2 = comparisonResult.player2.player}
		<section
			bind:this={comparisonSectionEl}
			tabindex="-1"
			aria-label="Head-to-head player comparison"
			class="bg-paper-2 border-t-2 border-rule-2 p-6 space-y-6 focus:outline-none"
		>
			<div class="flex items-center justify-between flex-wrap gap-3 border-b border-rule pb-4">
				<h2 class="text-xl font-display font-bold text-ink card-headline">Head-to-head player comparison</h2>
				<button
					type="button"
					onclick={() => (comparisonResult = null)}
					class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-3 text-ink-2 hover:text-ink text-sm font-semibold transition-colors whitespace-nowrap"
				>
					Close comparison
				</button>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
				<div class="border-t border-rule pt-4 flex items-center gap-4">
					<span class="num font-display font-bold text-2xl text-accent-text">
						#{p1.jersey_number}
					</span>
					<div>
						<h3 class="text-base font-bold text-ink card-headline">{p1.name}</h3>
						<p class="text-xs text-muted">{p1.position}, {p1.nationality}</p>
					</div>
				</div>

				<div class="border-t border-rule pt-4 flex items-center gap-4">
					<span class="num font-display font-bold text-2xl text-accent-text">
						#{p2.jersey_number}
					</span>
					<div>
						<h3 class="text-base font-bold text-ink card-headline">{p2.name}</h3>
						<p class="text-xs text-muted">{p2.position}, {p2.nationality}</p>
					</div>
				</div>
			</div>

			<!-- Semantic Comparison Metrics Table -->
			<div class="overflow-x-auto border-y border-rule">
				<table class="w-full border-collapse text-sm">
					<caption class="visually-hidden">
						Statistical comparison between {p1.name} and {p2.name}
					</caption>
					<thead>
						<tr class="border-b border-rule text-xs text-muted font-semibold">
							<th scope="col" class="py-2.5 text-left font-semibold">{p1.short_name}</th>
							<th scope="col" class="py-2.5 text-center font-semibold">Metric</th>
							<th scope="col" class="py-2.5 text-right font-semibold">{p2.short_name}</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-rule">
						<tr>
							<td class="py-2.5 num font-semibold text-ink">{p1.goals}</td>
							<th scope="row" class="py-2.5 text-center text-xs font-normal text-muted">Total goals</th>
							<td class="py-2.5 num font-semibold text-ink text-right">{p2.goals}</td>
						</tr>
						<tr>
							<td class="py-2.5 num font-semibold text-ink">{p1.assists}</td>
							<th scope="row" class="py-2.5 text-center text-xs font-normal text-muted">Total assists</th>
							<td class="py-2.5 num font-semibold text-ink text-right">{p2.assists}</td>
						</tr>
						<tr>
							<td class="py-2.5 num font-outlier font-semibold text-success">{comparisonResult.player1.goals_per_90}</td>
							<th scope="row" class="py-2.5 text-center text-xs font-normal text-muted">Goals per 90 min</th>
							<td class="py-2.5 num font-outlier font-semibold text-success text-right">{comparisonResult.player2.goals_per_90}</td>
						</tr>
						<tr>
							<td class="py-2.5 num font-outlier font-semibold text-accent-2">{comparisonResult.player1.minutes_per_contribution}m</td>
							<th scope="row" class="py-2.5 text-center text-xs font-normal text-muted">Minutes per G+A</th>
							<td class="py-2.5 num font-outlier font-semibold text-accent-2 text-right">{comparisonResult.player2.minutes_per_contribution}m</td>
						</tr>
						<tr>
							<td class="py-2.5 num font-outlier font-semibold text-ink">{comparisonResult.player1.discipline_score} / 10</td>
							<th scope="row" class="py-2.5 text-center text-xs font-normal text-muted">Fairplay rating</th>
							<td class="py-2.5 num font-outlier font-semibold text-ink text-right">{comparisonResult.player2.discipline_score} / 10</td>
						</tr>
					</tbody>
				</table>
			</div>

			<p class="text-sm text-ink-2">
				<strong class="text-ink font-semibold">Tactical verdict:</strong> {comparisonResult.comparison_summary}
			</p>
		</section>
	{/if}

	<!-- Position Filter Tabs -->
	<div class="flex items-center justify-between flex-wrap gap-3 border-b border-rule pb-4">
		<div class="flex items-center gap-2 flex-wrap">
			{#each ['all', 'Goalkeeper', 'Defender', 'Midfielder', 'Attacker'] as pos (pos)}
				{@const isSelected = selectedPosition === pos}
				{@const posLabel = pos === 'all' ? 'All Gunners' : pos + 's'}
				<button
					type="button"
					aria-pressed={isSelected}
					onclick={() => handlePositionChange(pos)}
					class="min-h-[44px] px-4 rounded-card text-sm font-semibold transition-colors border whitespace-nowrap {isSelected ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					{posLabel}
				</button>
			{/each}
		</div>

		<div role="status" aria-live="polite" class="num text-xs text-muted">
			{isLoading ? 'Filtering Arsenal squad…' : `${players.length} squad players`}
		</div>
	</div>

	{#if squadError}
		<StateBanner
			variant="error"
			title="Squad directory unavailable"
			message={squadError}
			busy={isLoading}
			onretry={() => loadSquad(selectedPosition)}
		/>
	{/if}

	<!-- Players Grid -->
	{#if isLoading && players.length === 0}
		<div role="status" class="py-12 text-muted text-sm">
			Loading Arsenal squad profiles…
		</div>
	{:else if players.length === 0 && !squadError}
		<StateBanner
			variant="empty"
			title="No squad players found"
			message="No Arsenal squad profiles matched the active position filter."
			retryLabel={selectedPosition !== 'all' ? 'Show all Gunners' : 'Retry'}
			onretry={() => handlePositionChange('all')}
		/>
	{:else if players.length > 0}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 {isLoading ? 'opacity-70 transition-opacity' : ''}">
			{#each players as player (player.id)}
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
									<span class="num font-display font-bold text-4xl text-accent-text">#{player.jersey_number}</span>
									<span class="font-display font-bold text-lg text-ink">{getInitials(player.name)}</span>
									<span class="text-xs text-muted">{player.position}</span>
								</div>
							{/if}
						</div>

						<div class="space-y-1.5">
							<div class="flex items-center justify-between text-xs text-muted">
								<span class="num font-outlier font-semibold text-accent-text">#{player.jersey_number}</span>
								<span>{player.position}</span>
							</div>

							<h3 class="text-base font-bold text-ink group-hover:text-accent-text transition-colors card-headline">{player.name}</h3>
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

					<!-- Footer & Compare Action (single dossier link per card avoids redundant tab stops) -->
					<div class="flex items-center justify-between text-xs gap-2">
						<span class="num text-muted">{player.minutes_played} mins</span>
						<button
							type="button"
							aria-pressed={isSelectedP1 || isSelectedP2}
							onclick={() => toggleCompare(player.id)}
							class="min-h-[44px] px-4 rounded-card text-xs font-semibold transition-colors border whitespace-nowrap {isSelectedP1 || isSelectedP2 ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
						>
							{compareBtnLabel}
						</button>
					</div>
				</article>
			{/each}
		</div>
	{/if}
</div>
