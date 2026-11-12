<script lang="ts">
	import { ApiError, submitPrediction, fetchLeaderboard } from '$lib/api/football';
	import type { UpcomingMatchPrediction, LeaderboardEntry } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let upcoming = $state<UpcomingMatchPrediction[]>([]);
	let leaderboard = $state<LeaderboardEntry[]>([]);
	let isSubmitting = $state<Record<string, boolean>>({});
	let predictionInputs = $state<Record<string, { home: number; away: number }>>({});
	let notificationMessage = $state<string | null>(null);
	let errorBanner = $state<{ message: string; isAuth?: boolean } | null>(null);

	let isInitialized = false;

	$effect(() => {
		if (!isInitialized && data.upcoming) {
			upcoming = data.upcoming;
			leaderboard = data.leaderboard;

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
		errorBanner = null;
		notificationMessage = null;

		if (!data.user || !data.session?.access_token) {
			errorBanner = {
				message: 'Please sign in to submit score predictions.',
				isAuth: true
			};
			return;
		}

		const target = upcoming.find((u) => u.match.id === matchId);
		if (target && !target.can_predict) {
			errorBanner = {
				message: 'Predictions are locked once kickoff has passed.',
				isAuth: false
			};
			return;
		}

		const scores = predictionInputs[matchId] || { home: 0, away: 0 };
		isSubmitting[matchId] = true;

		try {
			const res = await submitPrediction(
				{
					...(data.currentUserId ? { user_id: data.currentUserId } : {}),
					user_name: data.userName,
					user_club_id: data.userClubId,
					match_id: matchId,
					predicted_home_score: scores.home,
					predicted_away_score: scores.away
				},
				data.session?.access_token
			);

			if (res) {
				if (target) {
					target.user_prediction = res;
				}
				notificationMessage = `Score prediction (${scores.home}:${scores.away}) locked in.`;
				leaderboard = await fetchLeaderboard();
			}
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			errorBanner = {
				message: isAuth
					? 'Please sign in to submit score predictions.'
					: err instanceof ApiError
						? err.detail
						: 'Could not submit prediction. Please try again.',
				isAuth
			};
		} finally {
			isSubmitting[matchId] = false;
		}
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
	<title>Matchday Predictor & Supporter Leaderboard | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
		<div class="space-y-3">
			<h1>Matchday predictor</h1>
			<p class="lead text-ink-2">
				Test your football foresight on upcoming Arsenal fixtures, earn points, and climb the supporter leaderboard.
			</p>
		</div>

		<!-- Points System Reminder -->
		<div class="border-t border-rule pt-3 text-xs space-y-1">
			<span class="text-accent-2 font-bold block">Points scoring</span>
			<p class="text-ink-2">Exact scoreline: <strong class="text-success num font-outlier">3 pts</strong></p>
			<p class="text-muted">Correct outcome (W/D/L): <strong class="text-accent-2 num font-outlier">1 pt</strong></p>
		</div>
	</div>

	{#if notificationMessage}
		<div class="p-3.5 rounded-card bg-paper-2 border border-rule text-success text-xs flex items-center justify-between">
			<span>{notificationMessage}</span>
			<button type="button" onclick={() => (notificationMessage = null)} class="text-muted hover:text-ink font-semibold">Close</button>
		</div>
	{/if}

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<div class="flex items-center gap-3 flex-wrap">
				<span>{errorBanner.message}</span>
				{#if errorBanner.isAuth}
					<a href="/login" class="underline text-ink font-semibold hover:text-accent">Sign in</a>
				{/if}
			</div>
			<button type="button" onclick={() => (errorBanner = null)} class="text-muted hover:text-ink font-semibold shrink-0">Dismiss</button>
		</div>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
		<!-- Left 8 Cols: Upcoming Match Predictions Stream -->
		<div class="lg:col-span-8 space-y-6">
			<div class="flex items-center justify-between border-b border-rule pb-3">
				<h2 class="text-xl font-bold text-ink">Upcoming matchday fixtures</h2>
				<span class="text-xs num font-outlier text-muted">{upcoming.length} open for predictions</span>
			</div>

			{#if upcoming.length === 0}
				<div class="py-12 border-t border-rule text-muted text-sm">
					No upcoming matches scheduled for prediction right now.
				</div>
			{:else}
				<div class="divide-y divide-rule">
					{#each upcoming as item}
						{@const match = item.match}
						{@const hasPred = !!item.user_prediction}
						{@const isLocked = !item.can_predict}
						{@const btnLabel = isLocked ? 'Locked (kickoff passed)' : isSubmitting[match.id] ? 'Saving…' : hasPred ? 'Update prediction' : 'Lock in (3 pts)'}
						<article class="py-6 space-y-5">
							<!-- Fixture Info Header -->
							<div class="flex items-center justify-between text-xs">
								<span class="text-accent-2 font-semibold">
									{match.competition_name || 'Matchday'}
								</span>
								<span class="num font-outlier text-muted">
									{formatDate(match.utc_date)}
								</span>
							</div>

							<!-- Teams Matchup & Score Inputs -->
							<div class="grid grid-cols-7 gap-3 items-center py-4 border-y border-rule">
								<div class="col-span-3 text-right">
									<h3 class="text-base font-bold text-ink truncate">{match.home_team_name}</h3>
									<p class="text-xs text-muted">Home</p>
								</div>

								<div class="col-span-1 flex items-center justify-center gap-2 num font-outlier">
									<input
										type="number"
										min="0"
										max="20"
										disabled={isLocked}
										aria-label="Home team predicted goals"
										bind:value={predictionInputs[match.id].home}
										class="w-10 h-10 rounded-card bg-paper-2 border border-rule text-center text-sm font-bold text-ink disabled:opacity-50"
									/>
									<span class="text-muted font-bold">:</span>
									<input
										type="number"
										min="0"
										max="20"
										disabled={isLocked}
										aria-label="Away team predicted goals"
										bind:value={predictionInputs[match.id].away}
										class="w-10 h-10 rounded-card bg-paper-2 border border-rule text-center text-sm font-bold text-ink disabled:opacity-50"
									/>
								</div>

								<div class="col-span-3 text-left">
									<h3 class="text-base font-bold text-ink truncate">{match.away_team_name}</h3>
									<p class="text-xs text-muted">Away</p>
								</div>
							</div>

							<!-- Submission & Lock-in Button -->
							<div class="flex items-center justify-between text-xs">
								<div class="text-muted">
									{#if hasPred}
										<span class="text-success font-semibold num font-outlier">
											Predicted: {item.user_prediction?.predicted_home_score}:{item.user_prediction?.predicted_away_score}
										</span>
									{:else if isLocked}
										<span>Prediction window closed</span>
									{:else}
										<span>Not predicted yet</span>
									{/if}
								</div>

								<button
									type="button"
									onclick={() => handlePredict(match.id)}
									disabled={isLocked || isSubmitting[match.id]}
									class="h-9 px-4 rounded-card text-xs font-semibold transition-colors border disabled:opacity-50 {hasPred || isLocked ? 'bg-paper-2 text-ink border-rule hover:bg-paper-3' : 'bg-accent hover:opacity-95 text-accent-ink border-accent'}"
								>
									{btnLabel}
								</button>
							</div>
						</article>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Right 4 Cols: Supporter Leaderboard Widget -->
		<aside class="lg:col-span-4 border-t-2 border-rule-2 pt-5 space-y-5">
			<div class="border-b border-rule pb-3">
				<h2 class="text-lg font-bold text-ink">Supporter leaderboard</h2>
				<p class="text-xs text-muted">Rankings across all matchday predictors</p>
			</div>

			{#if leaderboard.length === 0}
				<p class="py-6 text-xs text-muted">No supporter predictions scored yet.</p>
			{:else}
				<div class="divide-y divide-rule text-xs">
					{#each leaderboard as entry}
						<div class="py-3 flex items-center justify-between gap-3">
							<div class="flex items-center gap-3 min-w-0">
								<span class="w-6 font-bold num font-outlier {entry.rank === 1 ? 'text-accent-2' : 'text-muted'}">
									#{entry.rank}
								</span>
								<div class="min-w-0">
									<a href="/supporters/{entry.user_name}" class="font-bold text-ink hover:text-accent transition-colors truncate block">
										{entry.user_name}
									</a>
									<p class="text-xs text-muted num font-outlier">
										{entry.exact_scores} exact hits ({entry.accuracy_rate}% acc)
									</p>
								</div>
							</div>

							<div class="text-right shrink-0">
								<span class="text-sm font-bold num font-outlier text-success">{entry.total_points}</span>
								<span class="text-xs text-muted"> pts</span>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</aside>
	</div>
</div>
