<script lang="ts">
	import { ApiError, submitPrediction, fetchLeaderboard } from '$lib/api/football';
	import { fetchPredictionHistory } from '$lib/api/community';
	import type {
		UpcomingMatchPrediction,
		LeaderboardEntry,
		PredictionHistoryItem
	} from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let upcoming = $state<UpcomingMatchPrediction[]>([]);
	let leaderboard = $state<LeaderboardEntry[]>([]);
	let history = $state<PredictionHistoryItem[]>([]);
	let isSubmitting = $state<Record<string, boolean>>({});
	let predictionInputs = $state<Record<string, { home: number; away: number }>>({});
	let notificationMessage = $state<string | null>(null);
	let errorBanner = $state<{ message: string; isAuth?: boolean } | null>(null);
	let nowMs = $state(Date.now());
	let leaderboardMode = $state<'all' | 'seasonal'>('all');
	let selectedCampaign = $state<string>('');
	let isLoadingLeaderboard = $state(false);

	let isSignedIn = $derived(Boolean(data.user && data.session?.access_token));

	let campaignOptions = $derived.by(() => {
		const seen = new Map<string, { value: string; label: string; startYear: number; isCurrent: boolean }>();
		for (const s of data.seasons || []) {
			if (!s.start_year || !s.end_year) continue;
			const value = `${s.start_year}-${s.end_year}`;
			const existing = seen.get(value);
			const isCurrent = Boolean(s.is_current || existing?.isCurrent);
			seen.set(value, {
				value,
				label: isCurrent ? `${value} (Current)` : value,
				startYear: s.start_year,
				isCurrent
			});
		}
		return Array.from(seen.values()).sort((a, b) => b.startYear - a.startYear);
	});

	let selectedLeaderboardSeason = $derived(
		leaderboardMode === 'seasonal' ? selectedCampaign || campaignOptions[0]?.value : undefined
	);

	$effect(() => {
		if (campaignOptions.length > 0 && !campaignOptions.some((c) => c.value === selectedCampaign)) {
			const currentOpt = campaignOptions.find((c) => c.isCurrent) || campaignOptions[0];
			selectedCampaign = currentOpt.value;
		}
	});

	$effect(() => {
		const intervalId = setInterval(() => {
			nowMs = Date.now();
		}, 60000);
		return () => {
			clearInterval(intervalId);
		};
	});

	$effect(() => {
		upcoming = data.upcoming || [];
		leaderboard = data.leaderboard || [];
		history = data.history || [];

		const nextInputs: Record<string, { home: number; away: number }> = {};
		for (const item of upcoming) {
			if (item.user_prediction) {
				nextInputs[item.match.id] = {
					home: item.user_prediction.predicted_home_score,
					away: item.user_prediction.predicted_away_score
				};
			} else {
				nextInputs[item.match.id] = { home: 1, away: 0 };
			}
		}
		predictionInputs = nextInputs;
	});

	function isKickoffPassed(utcDate: string, currentMs: number): boolean {
		const targetMs = new Date(utcDate).getTime();
		if (Number.isNaN(targetMs)) return false;
		return targetMs <= currentMs;
	}

	function formatCountdown(utcDate: string, canPredict: boolean, currentMs: number): string {
		if (!canPredict || isKickoffPassed(utcDate, currentMs)) {
			return 'Locked';
		}
		const targetMs = new Date(utcDate).getTime();
		const diffMs = targetMs - currentMs;
		const totalMinutes = Math.floor(diffMs / 60000);
		if (totalMinutes < 1) {
			return 'Kickoff < 1m';
		}
		const days = Math.floor(totalMinutes / (60 * 24));
		const hours = Math.floor((totalMinutes % (60 * 24)) / 60);
		const minutes = totalMinutes % 60;
		if (days > 0) {
			return `Kickoff in ${days}d ${hours}h`;
		}
		if (hours > 0) {
			return `Kickoff in ${hours}h ${minutes}m`;
		}
		return `Kickoff in ${minutes}m`;
	}

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
		if (target && (!target.can_predict || isKickoffPassed(target.match.utc_date, nowMs))) {
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
				const [nextLeaderboard, nextHistory] = await Promise.all([
					fetchLeaderboard(undefined, selectedLeaderboardSeason),
					fetchPredictionHistory(data.session?.access_token)
				]);
				leaderboard = nextLeaderboard;
				history = nextHistory;
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

	async function refreshLeaderboard(seasonParam?: string) {
		isLoadingLeaderboard = true;
		try {
			leaderboard = await fetchLeaderboard(undefined, seasonParam);
		} finally {
			isLoadingLeaderboard = false;
		}
	}

	async function setLeaderboardMode(mode: 'all' | 'seasonal') {
		leaderboardMode = mode;
		const seasonParam =
			mode === 'seasonal' ? selectedCampaign || campaignOptions[0]?.value : undefined;
		await refreshLeaderboard(seasonParam);
	}

	async function handleCampaignChange() {
		if (leaderboardMode !== 'seasonal') {
			leaderboardMode = 'seasonal';
		}
		await refreshLeaderboard(selectedCampaign);
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

	function formatMatchStatus(status: string): string {
		switch (status) {
			case 'FINISHED':
				return 'Finished';
			case 'IN_PLAY':
			case 'LIVE':
				return 'In play';
			case 'SCHEDULED':
				return 'Scheduled';
			default:
				return status;
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

	{#if !isSignedIn}
		<section class="border border-rule bg-paper-2 p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
			<div class="space-y-1">
				<h2 class="text-base font-bold text-ink">Guest preview mode</h2>
				<p class="text-xs text-ink-2">
					Browse upcoming Arsenal fixtures and the supporter standings freely. Sign in to lock in your scoreline predictions and track your points history.
				</p>
			</div>
			<div class="flex items-center gap-3 shrink-0">
				<a
					href="/login"
					class="inline-flex items-center h-9 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
				>
					Sign in
				</a>
				<a
					href="/signup"
					class="inline-flex items-center h-9 px-4 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink font-semibold text-xs transition-colors"
				>
					Create account
				</a>
			</div>
		</section>
	{/if}

	{#if notificationMessage}
		<div aria-live="polite" class="p-3.5 rounded-card bg-paper-2 border border-rule text-success text-xs flex items-center justify-between">
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
		<div class="lg:col-span-8 space-y-10">
			<section class="space-y-6">
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
							{@const isLocked = !item.can_predict || isKickoffPassed(match.utc_date, nowMs)}
							{@const countdownLabel = formatCountdown(match.utc_date, item.can_predict, nowMs)}
							{@const btnLabel = isLocked ? 'Locked (kickoff passed)' : isSubmitting[match.id] ? 'Saving…' : hasPred ? 'Update prediction' : 'Lock in (3 pts)'}
							<article class="py-6 space-y-5">
								<!-- Fixture Info Header -->
								<div class="flex items-center justify-between gap-3 flex-wrap text-xs">
									<span class="text-accent-2 font-semibold">
										{match.competition_name || 'Matchday'}
									</span>
									<div class="flex items-center gap-3 num font-outlier">
										<span class="text-muted">
											{formatDate(match.utc_date)}
										</span>
										<span
											class="px-2 py-0.5 rounded-card border border-rule {isLocked ? 'bg-paper-3 text-muted' : 'bg-paper-2 text-ink-2'}"
										>
											{countdownLabel}
										</span>
									</div>
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
								<div class="flex items-center justify-between text-xs gap-3 flex-wrap">
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
			</section>

			{#if isSignedIn}
				<section aria-labelledby="prediction-history-heading" class="space-y-5 border-t-2 border-rule-2 pt-8">
					<div class="flex items-center justify-between border-b border-rule pb-3">
						<h2 id="prediction-history-heading" class="text-xl font-bold text-ink">
							My Settled &amp; Active Predictions
						</h2>
						<span class="text-xs num font-outlier text-muted">{history.length} total</span>
					</div>

					{#if history.length === 0}
						<p class="py-6 text-xs text-muted">
							You have not submitted any matchday predictions yet. Lock in a scoreline above to begin tracking your record.
						</p>
					{:else}
						<div class="divide-y divide-rule border-b border-rule">
							{#each history as item}
								{@const hasActual = item.match_status === 'FINISHED' && item.home_score !== null && item.home_score !== undefined && item.away_score !== null && item.away_score !== undefined}
								{@const isGraded = item.points_awarded !== null && item.points_awarded !== undefined}
								<div class="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
									<div class="space-y-1 min-w-0">
										<div class="flex items-center gap-2.5 flex-wrap">
											<span class="text-accent-2 font-semibold">{item.competition}</span>
											<span class="text-muted num font-outlier">{formatDate(item.utc_date)}</span>
											<span class="px-2 py-0.5 rounded-card border border-rule bg-paper-2 text-ink-2">
												{formatMatchStatus(item.match_status)}
											</span>
										</div>
										<p class="text-sm font-bold text-ink truncate">
											{item.home_team} vs {item.away_team}
										</p>
									</div>

									<div class="flex items-center gap-5 shrink-0 num font-outlier">
										<div>
											<span class="text-muted block">Predicted</span>
											<span class="text-sm font-bold text-ink">
												{item.predicted_home_score}:{item.predicted_away_score}
											</span>
										</div>
										<div>
											<span class="text-muted block">Actual</span>
											<span class="text-sm font-bold text-ink-2">
												{hasActual ? `${item.home_score}:${item.away_score}` : '—'}
											</span>
										</div>
										<div class="text-right min-w-[68px]">
											<span class="text-muted block">Points</span>
											{#if isGraded}
												<span
													class="text-sm font-bold {item.points_awarded === 3 ? 'text-success' : item.points_awarded === 1 ? 'text-accent-2' : 'text-muted'}"
												>
													{item.points_awarded} pts
												</span>
											{:else}
												<span class="text-sm font-semibold text-muted">Pending</span>
											{/if}
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</section>
			{/if}
		</div>

		<!-- Right 4 Cols: Supporter Leaderboard Widget -->
		<aside class="lg:col-span-4 border-t-2 border-rule-2 pt-5 space-y-5">
			<div class="border-b border-rule pb-3 space-y-3">
				<div>
					<h2 class="text-lg font-bold text-ink">Supporter leaderboard</h2>
					<p class="text-xs text-muted">
						{leaderboardMode === 'all'
							? 'All-time rankings across all matchday predictors'
							: `Campaign standings for ${selectedCampaign || 'selected season'}`}
					</p>
				</div>

				<div class="flex items-center gap-2">
					<button
						type="button"
						aria-pressed={leaderboardMode === 'all'}
						onclick={() => setLeaderboardMode('all')}
						class="flex-1 h-8 px-3 rounded-card text-xs font-semibold transition-colors border {leaderboardMode === 'all' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						All-time
					</button>
					<button
						type="button"
						aria-pressed={leaderboardMode === 'seasonal'}
						onclick={() => setLeaderboardMode('seasonal')}
						class="flex-1 h-8 px-3 rounded-card text-xs font-semibold transition-colors border {leaderboardMode === 'seasonal' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						Seasonal
					</button>
				</div>

				{#if leaderboardMode === 'seasonal' && campaignOptions.length > 0}
					<div class="space-y-1">
						<label for="leaderboard-season-select" class="block text-xs font-semibold text-ink-2">
							Campaign season
						</label>
						<select
							id="leaderboard-season-select"
							bind:value={selectedCampaign}
							onchange={handleCampaignChange}
							class="w-full h-9 bg-paper-2 border border-rule rounded-card px-2.5 text-xs text-ink"
						>
							{#each campaignOptions as opt}
								<option value={opt.value}>{opt.label}</option>
							{/each}
						</select>
					</div>
				{/if}
			</div>

			{#if isLoadingLeaderboard}
				<p aria-live="polite" class="py-6 text-xs text-muted">Updating leaderboard standings…</p>
			{:else if leaderboard.length === 0}
				<p class="py-6 text-xs text-muted">
					{leaderboardMode === 'all'
						? 'No supporter predictions scored yet.'
						: 'No supporter predictions scored for this campaign yet.'}
				</p>
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
