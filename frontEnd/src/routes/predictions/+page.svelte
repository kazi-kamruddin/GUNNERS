<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { submitPrediction, fetchLeaderboard } from '$lib/api/football';
	import type { UpcomingMatchPrediction, LeaderboardEntry } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let upcoming = $state<UpcomingMatchPrediction[]>([]);
	let leaderboard = $state<LeaderboardEntry[]>([]);
	let selectedLeaderboardClub = $state<string>('all');
	let isSubmitting = $state<Record<string, boolean>>({});
	let predictionInputs = $state<Record<string, { home: number; away: number }>>({});
	let notificationMessage = $state<string | null>(null);

	let isInitialized = false;
	const viewingClub = $derived(themeState.currentTheme);
	const clubList = Object.values(CLUBS);

	$effect(() => {
		if (!isInitialized && data.upcoming) {
			upcoming = data.upcoming;
			leaderboard = data.leaderboard;

			// Pre-fill inputs with existing predictions if any
			for (const item of data.upcoming) {
				if (item.user_prediction) {
					predictionInputs[item.match.id] = {
						home: item.user_prediction.predicted_home_score,
						away: item.user_prediction.predicted_away_score
					};
				} else {
					predictionInputs[item.match.id] = { home: 1, away: 0 };
				}
			}
			isInitialized = true;
		}
	});

	async function handlePredict(matchId: string) {
		const scores = predictionInputs[matchId] || { home: 0, away: 0 };
		isSubmitting[matchId] = true;
		notificationMessage = null;

		try {
			const res = await submitPrediction({
				user_id: data.currentUserId,
				user_name: data.userName,
				user_club_id: data.userClubId,
				match_id: matchId,
				predicted_home_score: scores.home,
				predicted_away_score: scores.away
			});

			if (res) {
				const target = upcoming.find((u) => u.match.id === matchId);
				if (target) {
					target.user_prediction = res;
				}
				notificationMessage = `Score prediction (${scores.home} - ${scores.away}) locked in successfully!`;
				// Refresh leaderboard
				leaderboard = await fetchLeaderboard(selectedLeaderboardClub !== 'all' ? selectedLeaderboardClub : undefined);
			}
		} finally {
			isSubmitting[matchId] = false;
		}
	}

	async function handleFilterLeaderboard(clubId: string) {
		selectedLeaderboardClub = clubId;
		const filter = clubId !== 'all' ? clubId : undefined;
		leaderboard = await fetchLeaderboard(filter);
	}

	function formatDate(utcDate: string): string {
		try {
			const d = new Date(utcDate);
			return d.toLocaleDateString(undefined, {
				weekday: 'short',
				month: 'short',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return utcDate;
		}
	}
</script>

<svelte:head>
	<title>Matchday Predictor & Supporter Leaderboard | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-10">
	<!-- Page Header -->
	<div class="border-b border-[#1e2430] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
				Zero-Money Fan Prediction Game
			</div>
			<h1 class="text-2xl sm:text-3xl font-black text-white uppercase tracking-tight">Matchday Predictor</h1>
			<p class="text-xs sm:text-sm text-gray-400 mt-1">
				Test your football foresight on upcoming matches. Earn points and climb your club and global supporter leaderboards.
			</p>
		</div>

		<!-- Points System Reminder Pill -->
		<div class="p-3 rounded-lg border border-[#1e2430] bg-[#0d1017] text-xs font-mono space-y-1">
			<span class="text-amber-400 font-bold block uppercase text-[10px]">Points Scoring:</span>
			<p class="text-gray-300">🎯 Exact Scoreline: <strong class="text-emerald-400">3 pts</strong></p>
			<p class="text-gray-400">⚽ Correct Outcome (W/D/L): <strong class="text-amber-400">1 pt</strong></p>
		</div>
	</div>

	{#if notificationMessage}
		<div class="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 text-xs font-mono flex items-center justify-between">
			<span>✓ {notificationMessage}</span>
			<button type="button" onclick={() => (notificationMessage = null)} class="text-emerald-400 hover:text-white">✕</button>
		</div>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
		<!-- Left 2 Cols: Upcoming Match Predictions Stream -->
		<div class="lg:col-span-2 space-y-4">
			<div class="flex items-center justify-between mb-2">
				<h2 class="text-base font-bold text-white uppercase tracking-wider">Upcoming Matchday Fixtures</h2>
				<span class="text-xs font-mono text-gray-400">{upcoming.length} open for predictions</span>
			</div>

			{#if upcoming.length === 0}
				<div class="py-16 text-center border border-dashed border-[#1e2430] rounded-xl text-gray-500 text-xs">
					No upcoming matches scheduled for prediction right now.
				</div>
			{:else}
				<div class="space-y-4">
					{#each upcoming as item}
						{@const match = item.match}
						{@const hasPred = !!item.user_prediction}
						{@const homeScore = predictionInputs[match.id]?.home ?? 0}
						{@const awayScore = predictionInputs[match.id]?.away ?? 0}
						<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-4">
							<!-- Fixture Info Header -->
							<div class="flex items-center justify-between text-xs">
								<span class="font-mono text-amber-400 font-bold uppercase tracking-wider text-[11px]">
									{match.competition_name || 'Matchday'}
								</span>
								<span class="font-mono text-gray-400 text-[11px]">
									{formatDate(match.utc_date)}
								</span>
							</div>

							<!-- Teams Matchup & Score Inputs -->
							<div class="grid grid-cols-7 gap-2 items-center bg-[#0d1017] p-4 rounded-xl border border-[#1e2430]">
								<!-- Home Team -->
								<div class="col-span-3 text-right">
									<h4 class="text-sm font-bold text-white truncate">{match.home_team_name}</h4>
									<p class="text-[10px] text-gray-500 uppercase">Home</p>
								</div>

								<!-- Score Predictor Box -->
								<div class="col-span-1 flex items-center justify-center gap-1.5 font-mono">
									<input
										type="number"
										min="0"
										max="20"
										bind:value={predictionInputs[match.id].home}
										class="w-8 h-8 rounded bg-[#12161f] border border-[#1e2430] text-center text-sm font-bold text-white focus:outline-none focus:border-amber-400"
									/>
									<span class="text-gray-500 font-bold">:</span>
									<input
										type="number"
										min="0"
										max="20"
										bind:value={predictionInputs[match.id].away}
										class="w-8 h-8 rounded bg-[#12161f] border border-[#1e2430] text-center text-sm font-bold text-white focus:outline-none focus:border-amber-400"
									/>
								</div>

								<!-- Away Team -->
								<div class="col-span-3 text-left">
									<h4 class="text-sm font-bold text-white truncate">{match.away_team_name}</h4>
									<p class="text-[10px] text-gray-500 uppercase">Away</p>
								</div>
							</div>

							<!-- Submission & Lock-in Button -->
							<div class="flex items-center justify-between text-xs pt-1">
								<div class="text-[11px] text-gray-500 font-mono">
									{#if hasPred}
										<span class="text-emerald-400 font-bold">
											✓ Predicted: {item.user_prediction?.predicted_home_score} - {item.user_prediction?.predicted_away_score}
										</span>
									{:else}
										<span>Not predicted yet</span>
									{/if}
								</div>

								<button
									type="button"
									onclick={() => handlePredict(match.id)}
									disabled={isSubmitting[match.id]}
									class="px-4 py-1.5 rounded-lg text-xs font-bold transition shadow-sm border {hasPred ? 'bg-white/10 text-gray-200 border-[#1e2430] hover:text-white' : 'bg-amber-500 hover:bg-amber-400 text-black border-amber-400'}"
								>
									{isSubmitting[match.id] ? 'Saving...' : hasPred ? 'Update Prediction' : 'Lock In (3 pts)'}
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Right Col: Supporter Leaderboard Widget -->
		<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-4">
			<div class="border-b border-[#1e2430] pb-3">
				<h3 class="text-sm font-bold text-white uppercase tracking-wider">Supporter Leaderboard</h3>
				<p class="text-[11px] text-gray-400">Rankings across all predictors</p>
			</div>

			<!-- Club Filter Pill Bar -->
			<div class="flex flex-wrap gap-1">
				<button
					type="button"
					onclick={() => handleFilterLeaderboard('all')}
					class="text-[10px] px-2 py-0.5 rounded transition {selectedLeaderboardClub === 'all' ? 'bg-amber-400 text-black font-bold' : 'bg-[#0d1017] text-gray-400 hover:text-white'}"
				>
					Global
				</button>
				{#each clubList as club}
					<button
						type="button"
						onclick={() => handleFilterLeaderboard(club.id)}
						class="text-[10px] px-2 py-0.5 rounded transition {selectedLeaderboardClub === club.id ? 'bg-white/20 text-white font-bold' : 'bg-[#0d1017] text-gray-400 hover:text-white'}"
					>
						{club.short_name}
					</button>
				{/each}
			</div>

			<!-- Leaderboard Table -->
			<div class="divide-y divide-[#1e2430] text-xs">
				{#each leaderboard as entry}
					{@const club = CLUBS[entry.user_club_id] || CLUBS.arsenal}
					<div class="py-2.5 flex items-center justify-between">
						<div class="flex items-center gap-2.5">
							<span class="w-5 text-center font-bold font-mono text-xs {entry.rank === 1 ? 'text-amber-400' : entry.rank === 2 ? 'text-gray-300' : entry.rank === 3 ? 'text-amber-600' : 'text-gray-500'}">
								{entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : `#${entry.rank}`}
							</span>
							<div>
								<div class="flex items-center gap-1.5">
									<a href="/supporters/{entry.user_name}" class="font-bold text-white hover:text-amber-400 transition truncate max-w-[120px]">
										{entry.user_name}
									</a>
									<span class="w-2 h-2 rounded-full" style="background-color: {club.primary_color}"></span>
								</div>
								<p class="text-[10px] text-gray-500 font-mono">
									{entry.exact_scores} exact hits • {entry.accuracy_rate}% acc
								</p>
							</div>
						</div>

						<div class="text-right">
							<span class="text-sm font-black font-mono text-emerald-400">{entry.total_points}</span>
							<p class="text-[10px] text-gray-500 font-mono">pts</p>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>
