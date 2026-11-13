<script lang="ts">
	import { untrack } from 'svelte';
	import {
		ApiError,
		submitPrediction,
		fetchUpcomingPredictionsStrict,
		fetchLeaderboardStrict,
		getApiErrorMessage
	} from '$lib/api/football';
	import { fetchPredictionHistoryResult } from '$lib/api/community';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { formatMatchDateTime } from '$lib/utils/format';
	import type {
		UpcomingMatchPrediction,
		LeaderboardEntry,
		PredictionHistoryItem
	} from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	function buildInputsMap(
		items: UpcomingMatchPrediction[],
		existing: Record<string, { home: number; away: number }> = {},
		dirty: Record<string, boolean> = {}
	): Record<string, { home: number; away: number }> {
		const next: Record<string, { home: number; away: number }> = {};
		for (const item of items) {
			const id = item.match.id;
			if (dirty[id] && existing[id]) {
				next[id] = existing[id];
			} else if (item.user_prediction) {
				next[id] = {
					home: clampScore(item.user_prediction.predicted_home_score),
					away: clampScore(item.user_prediction.predicted_away_score)
				};
			} else if (existing[id]) {
				next[id] = existing[id];
			} else {
				next[id] = { home: 1, away: 0 };
			}
		}
		return next;
	}

	function clampScore(value: unknown): number {
		const n = typeof value === 'number' ? value : Number.parseInt(String(value ?? ''), 10);
		if (!Number.isFinite(n)) return 0;
		return Math.max(0, Math.min(20, Math.trunc(n)));
	}

	let upcoming = $state<UpcomingMatchPrediction[]>(untrack(() => data.upcoming || []));
	let upcomingError = $state<string | null>(untrack(() => data.upcomingError ?? null));
	let leaderboard = $state<LeaderboardEntry[]>(untrack(() => data.leaderboard || []));
	let leaderboardError = $state<string | null>(untrack(() => data.leaderboardError ?? null));
	let history = $state<PredictionHistoryItem[]>(untrack(() => data.history || []));
	let historyError = $state<string | null>(untrack(() => data.historyError ?? null));

	let dirtyInputs = $state<Record<string, boolean>>({});
	let predictionInputs = $state<Record<string, { home: number; away: number }>>(
		untrack(() => buildInputsMap(data.upcoming || []))
	);

	let isSubmitting = $state<Record<string, boolean>>({});
	let isRetryingUpcoming = $state(false);
	let isRetryingHistory = $state(false);
	let isLoadingLeaderboard = $state(false);

	let notificationMessage = $state<string | null>(null);
	let errorBanner = $state<{ message: string; isAuth?: boolean } | null>(null);
	let perMatchError = $state<Record<string, { message: string; isAuth?: boolean }>>({});
	let perMatchSuccess = $state<Record<string, string>>({});

	let nowMs = $state(Date.now());
	let leaderboardMode = $state<'all' | 'seasonal'>('all');
	let selectedCampaign = $state<string>('');
	let historyFilter = $state<'all' | 'graded' | 'pending'>('all');

	let leaderboardSeq = 0;
	let leaderboardAbort: AbortController | null = null;
	let syncedUserId = untrack(() => data.currentUserId ?? null);

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

	let openFixturesCount = $derived(
		upcoming.filter((u) => u.can_predict && !isKickoffPassed(u.match.utc_date, nowMs)).length
	);

	let hasImminentKickoff = $derived.by(() =>
		upcoming.some((u) => {
			if (!u.can_predict) return false;
			const targetMs = new Date(u.match.utc_date).getTime();
			if (Number.isNaN(targetMs)) return false;
			const diff = targetMs - nowMs;
			return diff > 0 && diff <= 120_000;
		})
	);

	let filteredHistory = $derived.by(() => {
		if (historyFilter === 'all') return history;
		if (historyFilter === 'graded') {
			return history.filter((item) => item.points_awarded !== null && item.points_awarded !== undefined);
		}
		return history.filter((item) => item.points_awarded === null || item.points_awarded === undefined);
	});

	$effect(() => {
		if (campaignOptions.length > 0 && !campaignOptions.some((c) => c.value === selectedCampaign)) {
			const currentOpt = campaignOptions.find((c) => c.isCurrent) || campaignOptions[0];
			selectedCampaign = currentOpt.value;
		}
	});

	$effect(() => {
		const intervalMs = hasImminentKickoff ? 1000 : 30000;
		const intervalId = setInterval(() => {
			nowMs = Date.now();
		}, intervalMs);
		return () => {
			clearInterval(intervalId);
		};
	});

	$effect(() => {
		const nextUpcoming = data.upcoming || [];
		const nextUpcomingError = data.upcomingError ?? null;
		const nextLeaderboard = data.leaderboard || [];
		const nextLeaderboardError = data.leaderboardError ?? null;
		const nextHistory = data.history || [];
		const nextHistoryError = data.historyError ?? null;
		const nextUserId = data.currentUserId ?? null;

		untrack(() => {
			const userChanged = nextUserId !== syncedUserId;
			if (userChanged) {
				syncedUserId = nextUserId;
				dirtyInputs = {};
			}

			upcoming = nextUpcoming;
			upcomingError = nextUpcomingError;
			if (leaderboardMode === 'all') {
				leaderboard = nextLeaderboard;
				leaderboardError = nextLeaderboardError;
			}
			history = nextHistory;
			historyError = nextHistoryError;
			predictionInputs = buildInputsMap(nextUpcoming, predictionInputs, userChanged ? {} : dirtyInputs);
		});
	});

	function isKickoffPassed(utcDate: string, currentMs: number): boolean {
		const targetMs = new Date(utcDate).getTime();
		if (Number.isNaN(targetMs)) return false;
		return targetMs <= currentMs;
	}

	function isUrgentCountdown(utcDate: string, canPredict: boolean, currentMs: number): boolean {
		if (!canPredict || isKickoffPassed(utcDate, currentMs)) return false;
		const targetMs = new Date(utcDate).getTime();
		if (Number.isNaN(targetMs)) return false;
		const diffMs = targetMs - currentMs;
		return diffMs > 0 && diffMs < 3_600_000;
	}

	function formatCountdown(utcDate: string, canPredict: boolean, currentMs: number): string {
		if (!canPredict || isKickoffPassed(utcDate, currentMs)) {
			return 'Locked · Kickoff passed';
		}
		const targetMs = new Date(utcDate).getTime();
		const diffMs = targetMs - currentMs;
		const totalSeconds = Math.max(0, Math.floor(diffMs / 1000));
		if (totalSeconds < 60) {
			return `Kickoff in ${totalSeconds}s`;
		}
		const totalMinutes = Math.floor(totalSeconds / 60);
		if (totalMinutes < 2) {
			const remSeconds = totalSeconds % 60;
			return `Kickoff in 1m ${remSeconds}s`;
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

	function getScores(item: UpcomingMatchPrediction): { home: number; away: number } {
		return (
			predictionInputs[item.match.id] ?? {
				home: clampScore(item.user_prediction?.predicted_home_score ?? 1),
				away: clampScore(item.user_prediction?.predicted_away_score ?? 0)
			}
		);
	}

	function setScore(matchId: string, side: 'home' | 'away', rawValue: unknown) {
		const current = predictionInputs[matchId] ?? { home: 1, away: 0 };
		const nextVal = clampScore(rawValue);
		predictionInputs = {
			...predictionInputs,
			[matchId]: {
				...current,
				[side]: nextVal
			}
		};
		dirtyInputs = { ...dirtyInputs, [matchId]: true };
		if (perMatchError[matchId]) {
			const copy = { ...perMatchError };
			delete copy[matchId];
			perMatchError = copy;
		}
	}

	function stepScore(matchId: string, side: 'home' | 'away', delta: number) {
		const current = predictionInputs[matchId] ?? { home: 1, away: 0 };
		setScore(matchId, side, current[side] + delta);
	}

	function clearMatchError(matchId: string) {
		if (!perMatchError[matchId]) return;
		const copy = { ...perMatchError };
		delete copy[matchId];
		perMatchError = copy;
	}

	async function handlePredict(matchId: string) {
		errorBanner = null;
		notificationMessage = null;
		clearMatchError(matchId);

		if (!data.user || !data.session?.access_token) {
			const authMsg = {
				message: 'Please sign in to submit score predictions.',
				isAuth: true
			};
			errorBanner = authMsg;
			perMatchError = { ...perMatchError, [matchId]: authMsg };
			return;
		}

		const target = upcoming.find((u) => u.match.id === matchId);
		if (target && (!target.can_predict || isKickoffPassed(target.match.utc_date, nowMs))) {
			const lockMsg = {
				message: 'Predictions are locked once kickoff has passed.',
				isAuth: false
			};
			errorBanner = lockMsg;
			perMatchError = { ...perMatchError, [matchId]: lockMsg };
			return;
		}

		const scores = predictionInputs[matchId] ?? { home: 0, away: 0 };
		const cleanHome = clampScore(scores.home);
		const cleanAway = clampScore(scores.away);
		isSubmitting = { ...isSubmitting, [matchId]: true };

		try {
			const res = await submitPrediction(
				{
					...(data.currentUserId ? { user_id: data.currentUserId } : {}),
					user_name: data.userName,
					user_club_id: data.userClubId,
					match_id: matchId,
					predicted_home_score: cleanHome,
					predicted_away_score: cleanAway
				},
				data.session?.access_token
			);

			if (res) {
				if (target) {
					target.user_prediction = res;
				}
				dirtyInputs = { ...dirtyInputs, [matchId]: false };
				predictionInputs = {
					...predictionInputs,
					[matchId]: {
						home: clampScore(res.predicted_home_score),
						away: clampScore(res.predicted_away_score)
					}
				};
				const lockedMsg = `Score prediction (${cleanHome}:${cleanAway}) locked in.`;
				notificationMessage = lockedMsg;
				perMatchSuccess = { ...perMatchSuccess, [matchId]: lockedMsg };

				const [lbSettled, histResult] = await Promise.allSettled([
					fetchLeaderboardStrict(undefined, selectedLeaderboardSeason),
					fetchPredictionHistoryResult(data.session?.access_token)
				]);

				if (lbSettled.status === 'fulfilled') {
					leaderboard = lbSettled.value;
					leaderboardError = null;
				} else {
					leaderboardError = getApiErrorMessage(
						lbSettled.reason,
						'Unable to refresh supporter leaderboard.'
					).detail;
				}

				if (histResult.status === 'fulfilled') {
					if (histResult.value.error) {
						historyError = histResult.value.error;
					} else {
						history = histResult.value.data;
						historyError = null;
					}
				} else {
					historyError = 'Unable to refresh prediction history.';
				}
			}
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			const errObj = {
				message: isAuth
					? 'Your session expired. Sign in to submit score predictions.'
					: err instanceof ApiError
						? err.detail
						: 'Could not submit prediction. Please try again.',
				isAuth
			};
			errorBanner = errObj;
			perMatchError = { ...perMatchError, [matchId]: errObj };
		} finally {
			isSubmitting = { ...isSubmitting, [matchId]: false };
		}
	}

	async function retryUpcoming() {
		isRetryingUpcoming = true;
		try {
			const nextUpcoming = await fetchUpcomingPredictionsStrict(
				data.currentUserId ?? undefined,
				data.session?.access_token
			);
			upcoming = nextUpcoming;
			upcomingError = null;
			predictionInputs = buildInputsMap(nextUpcoming, predictionInputs, dirtyInputs);
		} catch (err) {
			upcomingError = getApiErrorMessage(err, 'Unable to load upcoming matchday fixtures.').detail;
		} finally {
			isRetryingUpcoming = false;
		}
	}

	async function retryHistory() {
		isRetryingHistory = true;
		try {
			const res = await fetchPredictionHistoryResult(data.session?.access_token);
			if (res.error) {
				historyError = res.error;
			} else {
				history = res.data;
				historyError = null;
			}
		} finally {
			isRetryingHistory = false;
		}
	}

	async function refreshLeaderboard(seasonParam?: string) {
		leaderboardSeq += 1;
		const reqId = leaderboardSeq;
		leaderboardAbort?.abort();
		const controller = new AbortController();
		leaderboardAbort = controller;

		isLoadingLeaderboard = true;
		leaderboardError = null;
		try {
			const next = await fetchLeaderboardStrict(undefined, seasonParam, controller.signal);
			if (reqId !== leaderboardSeq) return;
			leaderboard = next;
			leaderboardError = null;
		} catch (err) {
			if (err instanceof DOMException && err.name === 'AbortError') return;
			if (reqId !== leaderboardSeq) return;
			leaderboardError = getApiErrorMessage(err, 'Unable to load supporter leaderboard.').detail;
		} finally {
			if (reqId === leaderboardSeq) {
				isLoadingLeaderboard = false;
			}
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
	<title>Matchday Predictor &amp; Supporter Leaderboard | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
		<div class="space-y-3">
			<h1 class="display-s text-ink">Matchday predictor</h1>
			<p class="lead text-ink-2">
				Test your football foresight on upcoming Arsenal fixtures, earn points, and climb the supporter leaderboard.
			</p>
		</div>

		<!-- Points System Reminder -->
		<div class="border-t border-rule pt-3 text-xs space-y-1">
			<span class="text-accent-2 font-bold block">Points scoring</span>
			<p class="text-ink-2">Exact scoreline: <strong class="text-success num font-outlier">3 pts</strong></p>
			<p class="text-ink-2">Correct outcome (W/D/L): <strong class="text-accent-2 num font-outlier">1 pt</strong></p>
			<p class="text-muted">Incorrect outcome: <strong class="text-ink-2 num font-outlier">0 pts</strong></p>
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
					href="/login?next=%2Fpredictions"
					class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
				>
					Sign in
				</a>
				<a
					href="/signup?next=%2Fpredictions"
					class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink font-semibold text-xs transition-colors"
				>
					Create account
				</a>
			</div>
		</section>
	{/if}

	{#if notificationMessage}
		<div aria-live="polite" class="p-3.5 rounded-card bg-paper-2 border border-rule text-success text-xs flex items-center justify-between gap-3">
			<span>{notificationMessage}</span>
			<button
				type="button"
				onclick={() => (notificationMessage = null)}
				class="min-h-[44px] px-2 text-ink-2 hover:text-ink font-semibold shrink-0"
			>
				Close
			</button>
		</div>
	{/if}

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<div class="flex items-center gap-3 flex-wrap">
				<span>{errorBanner.message}</span>
				{#if errorBanner.isAuth}
					<a href="/login?next=%2Fpredictions" class="underline text-ink font-semibold hover:text-accent-text">Sign in</a>
				{/if}
			</div>
			<button
				type="button"
				onclick={() => (errorBanner = null)}
				class="min-h-[44px] px-2 text-ink-2 hover:text-ink font-semibold shrink-0"
			>
				Dismiss
			</button>
		</div>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
		<!-- Left 8 Cols: Upcoming Match Predictions Stream -->
		<div class="lg:col-span-8 space-y-10">
			<section class="space-y-6">
				<div class="flex items-center justify-between gap-3 flex-wrap border-b border-rule pb-3">
					<h2 class="text-xl font-bold text-ink">Upcoming matchday fixtures</h2>
					<span class="text-xs num font-outlier text-muted">
						{openFixturesCount} open for predictions
						{#if upcoming.length > openFixturesCount}
							· {upcoming.length - openFixturesCount} locked
						{/if}
					</span>
				</div>

				{#if upcomingError}
					<StateBanner
						variant="error"
						title="Upcoming fixtures unavailable"
						message={upcomingError}
						onretry={retryUpcoming}
						busy={isRetryingUpcoming}
					/>
				{/if}

				{#if !upcomingError && upcoming.length === 0}
					<StateBanner
						variant="empty"
						title="No upcoming fixtures scheduled"
						message="No upcoming Arsenal matches are currently open for scoreline predictions. Check back before the next matchweek."
					/>
				{:else if upcoming.length > 0}
					<div class="divide-y divide-rule">
						{#each upcoming as item (item.match.id)}
							{@const match = item.match}
							{@const scores = getScores(item)}
							{@const hasPred = !!item.user_prediction}
							{@const isLocked = !item.can_predict || isKickoffPassed(match.utc_date, nowMs)}
							{@const isUrgent = isUrgentCountdown(match.utc_date, item.can_predict, nowMs)}
							{@const countdownLabel = formatCountdown(match.utc_date, item.can_predict, nowMs)}
							{@const btnLabel = isLocked
								? 'Locked (kickoff passed)'
								: isSubmitting[match.id]
									? 'Saving…'
									: !isSignedIn
										? 'Sign in to lock in'
										: hasPred
											? 'Update prediction'
											: 'Lock in (3 pts)'}
							{@const matchErr = perMatchError[match.id]}
							{@const matchOk = perMatchSuccess[match.id]}
							<article class="py-6 space-y-5">
								<!-- Fixture Info Header -->
								<div class="flex items-center justify-between gap-3 flex-wrap text-xs">
									<span class="text-accent-2 font-semibold">
										{match.competition_name || 'Matchday'}
									</span>
									<div class="flex items-center gap-3 flex-wrap num font-outlier">
										<span class="text-ink-2">
											{formatMatchDateTime(match.utc_date)}
										</span>
										<span
											class="px-2.5 py-1 rounded-card border {isLocked
												? 'border-rule-2 bg-paper-3 text-ink-2 font-semibold'
												: isUrgent
													? 'border-accent-2/50 bg-paper-2 text-accent-2 font-semibold'
													: 'border-rule bg-paper-2 text-ink-2'}"
										>
											{countdownLabel}
										</span>
									</div>
								</div>

								<!-- Teams Matchup & Score Inputs (mobile-first stacked -> sm 3-track grid) -->
								<div class="flex flex-col sm:grid sm:grid-cols-[1fr_auto_1fr] gap-4 items-center py-4 border-y border-rule">
									<div class="w-full sm:w-auto flex items-baseline justify-between sm:block sm:text-right min-w-0 gap-2">
										<h3 class="text-base font-bold text-ink line-clamp-2" title={match.home_team_name}>
											{match.home_team_name}
										</h3>
										<p class="text-xs text-muted shrink-0">Home</p>
									</div>

									<div class="flex items-center justify-center gap-2 num font-outlier shrink-0">
										<div class="inline-flex items-center border border-rule rounded-card bg-paper-2 overflow-hidden">
											<button
												type="button"
												disabled={isLocked || scores.home <= 0}
												onclick={() => stepScore(match.id, 'home', -1)}
												aria-label={`Decrease ${match.home_team_name} predicted goals`}
												class="min-h-[44px] min-w-[44px] flex items-center justify-center text-base font-bold text-ink-2 hover:bg-paper-3 hover:text-ink disabled:opacity-40 transition-colors"
											>
												−
											</button>
											<input
												type="number"
												inputmode="numeric"
												min="0"
												max="20"
												step="1"
												disabled={isLocked}
												aria-label={`${match.home_team_name} predicted goals`}
												value={scores.home}
												oninput={(e) => setScore(match.id, 'home', (e.currentTarget as HTMLInputElement).value)}
												class="w-11 min-h-[44px] bg-transparent border-x border-rule text-center text-sm font-bold text-ink disabled:opacity-50"
											/>
											<button
												type="button"
												disabled={isLocked || scores.home >= 20}
												onclick={() => stepScore(match.id, 'home', 1)}
												aria-label={`Increase ${match.home_team_name} predicted goals`}
												class="min-h-[44px] min-w-[44px] flex items-center justify-center text-base font-bold text-ink-2 hover:bg-paper-3 hover:text-ink disabled:opacity-40 transition-colors"
											>
												+
											</button>
										</div>

										<span class="text-muted font-bold px-0.5" aria-hidden="true">:</span>

										<div class="inline-flex items-center border border-rule rounded-card bg-paper-2 overflow-hidden">
											<button
												type="button"
												disabled={isLocked || scores.away <= 0}
												onclick={() => stepScore(match.id, 'away', -1)}
												aria-label={`Decrease ${match.away_team_name} predicted goals`}
												class="min-h-[44px] min-w-[44px] flex items-center justify-center text-base font-bold text-ink-2 hover:bg-paper-3 hover:text-ink disabled:opacity-40 transition-colors"
											>
												−
											</button>
											<input
												type="number"
												inputmode="numeric"
												min="0"
												max="20"
												step="1"
												disabled={isLocked}
												aria-label={`${match.away_team_name} predicted goals`}
												value={scores.away}
												oninput={(e) => setScore(match.id, 'away', (e.currentTarget as HTMLInputElement).value)}
												class="w-11 min-h-[44px] bg-transparent border-x border-rule text-center text-sm font-bold text-ink disabled:opacity-50"
											/>
											<button
												type="button"
												disabled={isLocked || scores.away >= 20}
												onclick={() => stepScore(match.id, 'away', 1)}
												aria-label={`Increase ${match.away_team_name} predicted goals`}
												class="min-h-[44px] min-w-[44px] flex items-center justify-center text-base font-bold text-ink-2 hover:bg-paper-3 hover:text-ink disabled:opacity-40 transition-colors"
											>
												+
											</button>
										</div>
									</div>

									<div class="w-full sm:w-auto flex items-baseline justify-between sm:block sm:text-left min-w-0 gap-2">
										<h3 class="text-base font-bold text-ink line-clamp-2" title={match.away_team_name}>
											{match.away_team_name}
										</h3>
										<p class="text-xs text-muted shrink-0">Away</p>
									</div>
								</div>

								<!-- Submission & Lock-in Button -->
								<div class="flex items-center justify-between text-xs gap-3 flex-wrap">
									<div class="text-muted flex items-center gap-3 flex-wrap">
										{#if hasPred}
											<span class="text-success font-semibold num font-outlier">
												Predicted: {item.user_prediction?.predicted_home_score}:{item.user_prediction?.predicted_away_score}
											</span>
										{:else if isLocked}
											<span class="text-ink-2">Prediction window closed</span>
										{:else}
											<span>Not predicted yet</span>
										{/if}
										<span class="text-rule-2" aria-hidden="true">·</span>
										<span class="num font-outlier">
											{item.total_predictions_count} {item.total_predictions_count === 1 ? 'prediction' : 'predictions'}
										</span>
									</div>

									<button
										type="button"
										onclick={() => handlePredict(match.id)}
										disabled={isLocked || isSubmitting[match.id]}
										class="min-h-[44px] px-4 rounded-card text-xs font-semibold transition-colors border disabled:opacity-50 {hasPred || isLocked || !isSignedIn
											? 'bg-paper-2 text-ink border-rule hover:bg-paper-3'
											: 'bg-accent hover:opacity-95 text-accent-ink border-accent'}"
									>
										{btnLabel}
									</button>
								</div>

								{#if matchErr}
									<div role="alert" class="p-3 border-y border-rule bg-paper-2 text-error text-xs flex items-center justify-between gap-3 flex-wrap">
										<div class="flex items-center gap-3 flex-wrap">
											<span>{matchErr.message}</span>
											{#if matchErr.isAuth}
												<a href="/login?next=%2Fpredictions" class="underline font-semibold text-ink hover:text-accent-text">
													Sign in
												</a>
											{/if}
										</div>
										<button
											type="button"
											onclick={() => clearMatchError(match.id)}
											class="min-h-[44px] px-2 text-ink-2 hover:text-ink font-semibold"
										>
											Dismiss
										</button>
									</div>
								{:else if matchOk}
									<p aria-live="polite" class="text-xs text-success font-semibold">
										{matchOk}
									</p>
								{/if}
							</article>
						{/each}
					</div>
				{/if}
			</section>

			{#if isSignedIn}
				<section aria-labelledby="prediction-history-heading" class="space-y-5 border-t-2 border-rule-2 pt-8">
					<div class="flex items-center justify-between gap-3 flex-wrap border-b border-rule pb-3">
						<h2 id="prediction-history-heading" class="text-xl font-bold text-ink">
							My Settled &amp; Active Predictions
						</h2>
						<div class="flex items-center gap-3 flex-wrap">
							{#if history.length > 5}
								<div class="flex items-center gap-1.5" role="group" aria-label="Filter prediction history">
									{#each [
										{ id: 'all', label: 'All' },
										{ id: 'graded', label: 'Graded' },
										{ id: 'pending', label: 'Pending' }
									] as opt (opt.id)}
										<button
											type="button"
											aria-pressed={historyFilter === opt.id}
											onclick={() => (historyFilter = opt.id as 'all' | 'graded' | 'pending')}
											class="min-h-[44px] px-3 rounded-card border text-xs font-semibold transition-colors {historyFilter === opt.id
												? 'bg-accent text-accent-ink border-accent'
												: 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
										>
											{opt.label}
										</button>
									{/each}
								</div>
							{/if}
							<span class="text-xs num font-outlier text-muted">{history.length} total</span>
						</div>
					</div>

					{#if historyError}
						<StateBanner
							variant="error"
							title="Prediction history unavailable"
							message={historyError}
							onretry={retryHistory}
							busy={isRetryingHistory}
						/>
					{/if}

					{#if !historyError && history.length === 0}
						<p class="py-6 text-xs text-muted">
							You have not submitted any matchday predictions yet. Lock in a scoreline above to begin tracking your record.
						</p>
					{:else if filteredHistory.length === 0 && history.length > 0}
						<p class="py-6 text-xs text-muted">
							No {historyFilter} predictions match the current filter.
						</p>
					{:else if filteredHistory.length > 0}
						<div class="divide-y divide-rule border-b border-rule">
							{#each filteredHistory as item (item.id)}
								{@const hasActual =
									item.match_status === 'FINISHED' &&
									item.home_score !== null &&
									item.home_score !== undefined &&
									item.away_score !== null &&
									item.away_score !== undefined}
								{@const isGraded = item.points_awarded !== null && item.points_awarded !== undefined}
								<div class="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
									<div class="space-y-1 min-w-0">
										<div class="flex items-center gap-2.5 flex-wrap">
											<span class="text-accent-2 font-semibold">{item.competition}</span>
											<span class="text-muted num font-outlier">{formatMatchDateTime(item.utc_date)}</span>
											<span class="px-2 py-0.5 rounded-card border border-rule bg-paper-2 text-ink-2">
												{formatMatchStatus(item.match_status)}
											</span>
										</div>
										<a
											href="/matches/{encodeURIComponent(item.match_id)}"
											class="text-sm font-bold text-ink hover:text-accent-text transition-colors line-clamp-2 inline-block"
										>
											{item.home_team} vs {item.away_team}
										</a>
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
													class="text-sm font-bold {item.points_awarded === 3
														? 'text-success'
														: item.points_awarded === 1
															? 'text-accent-2'
															: 'text-muted'}"
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
						class="flex-1 min-h-[44px] px-3 rounded-card text-xs font-semibold transition-colors border {leaderboardMode === 'all'
							? 'bg-accent text-accent-ink border-accent'
							: 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						All-time
					</button>
					<button
						type="button"
						aria-pressed={leaderboardMode === 'seasonal'}
						onclick={() => setLeaderboardMode('seasonal')}
						class="flex-1 min-h-[44px] px-3 rounded-card text-xs font-semibold transition-colors border {leaderboardMode === 'seasonal'
							? 'bg-accent text-accent-ink border-accent'
							: 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
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
							class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-2.5 text-xs text-ink"
						>
							{#each campaignOptions as opt (opt.value)}
								<option value={opt.value}>{opt.label}</option>
							{/each}
						</select>
					</div>
				{/if}
			</div>

			{#if leaderboardError}
				<StateBanner
					variant="error"
					title="Leaderboard unavailable"
					message={leaderboardError}
					onretry={() => refreshLeaderboard(selectedLeaderboardSeason)}
					busy={isLoadingLeaderboard}
				/>
			{/if}

			{#if isLoadingLeaderboard}
				<p aria-live="polite" class="py-6 text-xs text-muted">Updating leaderboard standings…</p>
			{:else if !leaderboardError && leaderboard.length === 0}
				<p class="py-6 text-xs text-muted">
					{leaderboardMode === 'all'
						? 'No supporter predictions scored yet.'
						: 'No supporter predictions scored for this campaign yet.'}
				</p>
			{:else if leaderboard.length > 0}
				<div class="divide-y divide-rule text-xs">
					{#each leaderboard as entry (entry.user_id || entry.user_name)}
						<div class="py-3 flex items-center justify-between gap-3">
							<div class="flex items-center gap-3 min-w-0">
								<span class="w-6 font-bold num font-outlier {entry.rank === 1 ? 'text-accent-2' : 'text-muted'}">
									#{entry.rank}
								</span>
								<div class="min-w-0">
									<a
										href="/supporters/{encodeURIComponent(entry.user_name)}"
										class="font-bold text-ink hover:text-accent-text transition-colors truncate block"
									>
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
