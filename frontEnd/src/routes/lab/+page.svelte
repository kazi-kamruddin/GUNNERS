<script lang="ts">
	import { untrack } from 'svelte';
	import { CLUBS } from '$lib/stores/theme.svelte';
	import { focusTrap } from '$lib/actions/focusTrap';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import {
		ApiError,
		queryAnalyticsStrict,
		createInsight,
		deleteInsight,
		fetchInsightsResult,
		fetchMultiSeasonTrendsStrict,
		fetchOpponentH2HStrict,
		comparePlayersStrict
	} from '$lib/api/football';
	import HistoricalPitchExplorer from '$lib/components/HistoricalPitchExplorer.svelte';
	import type {
		AnalyticsResponse,
		Insight,
		MultiSeasonTrendsResponse,
		OpponentH2HResponse,
		PlayerComparison,
		SeasonTrendItem
	} from '$lib/types/football';
	import type { PageProps } from './$types';

	type LabTab = 'query' | 'trends' | 'h2h' | 'squad' | 'pitch';
	type TrendMetricKey = 'win_rate' | 'points_per_game' | 'goals_per_match' | 'clean_sheet_rate';

	let { data }: PageProps = $props();

	const clubList = Object.values(CLUBS);

	function buildStamp(d: typeof data): string {
		return [
			d.initialTab,
			d.initialMetric,
			d.initialTeamIds.join(','),
			d.initialVenue,
			d.activeSeasonId,
			d.initialTrendsClub,
			d.initialTrendMetric,
			d.initialH2HClub,
			d.initialOpponentId,
			d.initialCompare1Id,
			d.initialCompare2Id
		].join('|');
	}

	function pickInitialTrendSeasonId(trends: MultiSeasonTrendsResponse | null): string | null {
		const rows = trends?.trends || [];
		const active = rows.filter((t) => t.matches_played > 0);
		if (active.length > 0) return active[active.length - 1].season_id;
		return rows[0]?.season_id || null;
	}

	let activeTab = $state<LabTab>(untrack(() => data.initialTab || 'query'));

	// Lens 1: Analytics Query state
	let mode = $state<'single' | 'comparison'>(
		untrack(() => (data.initialTeamIds.length > 1 ? 'comparison' : 'single'))
	);
	let team1 = $state<string>(untrack(() => data.initialTeamIds[0] || 'arsenal'));
	let team2 = $state<string>(untrack(() => data.initialTeamIds[1] || 'real-madrid'));
	let metric = $state<string>(untrack(() => data.initialMetric || 'win_rate'));
	let venue = $state<string>(untrack(() => data.initialVenue || 'all'));
	let selectedSeason = $state<string>(untrack(() => data.activeSeasonId || 'all'));
	let loading = $state(false);
	let result = $state<AnalyticsResponse | null>(untrack(() => data.initialResult));
	let queryError = $state<string | null>(untrack(() => data.initialQueryError ?? null));
	let insights = $state<Insight[]>(untrack(() => data.insights || []));
	let insightsError = $state<string | null>(untrack(() => data.insightsError ?? null));
	let isRetryingInsights = $state(false);
	let showAllInsights = $state(false);
	let confirmDeleteInsightId = $state<string | null>(null);
	let deletingInsightId = $state<string | null>(null);
	let seasons = $derived(data.seasons || []);

	// Track exact query parameters captured by `result` so Save as insight never pairs mismatched filters
	let resultSnapshotMeta = $state<{
		metric: string;
		team_ids: string[];
		venue: string;
		season_id: string;
	} | null>(
		untrack(() =>
			data.initialResult
				? {
						metric: data.initialMetric || 'win_rate',
						team_ids: data.initialTeamIds,
						venue: data.initialVenue || 'all',
						season_id: data.activeSeasonId || 'all'
					}
				: null
		)
	);

	// Lens 2: Multi-Season Trends state
	let trendsClub = $state<string>(untrack(() => data.initialTrendsClub || 'arsenal'));
	let trendsVenue = $state<string>(untrack(() => data.initialVenue || 'all'));
	let trendMetric = $state<TrendMetricKey>(untrack(() => data.initialTrendMetric || 'win_rate'));
	let trendsData = $state<MultiSeasonTrendsResponse | null>(untrack(() => data.initialTrends));
	let trendsError = $state<string | null>(untrack(() => data.initialTrendsError ?? null));
	let trendsLoading = $state(false);
	let selectedTrendSeasonId = $state<string | null>(
		untrack(() => pickInitialTrendSeasonId(data.initialTrends))
	);

	// Lens 3: Opponent H2H state
	let h2hClub = $state<string>(untrack(() => data.initialH2HClub || 'arsenal'));
	let h2hOpponent = $state<string>(untrack(() => data.initialOpponentId || 'chelsea'));
	let h2hVenue = $state<string>(untrack(() => data.initialVenue || 'all'));
	let h2hData = $state<OpponentH2HResponse | null>(untrack(() => data.initialH2H));
	let h2hError = $state<string | null>(untrack(() => data.initialH2HError ?? null));
	let h2hLoading = $state(false);

	// Lens 4: Squad H2H state
	let squadList = $derived(data.squad || []);
	let comparePlayer1Id = $state<string>(untrack(() => data.initialCompare1Id || 'ply_saka'));
	let comparePlayer2Id = $state<string>(untrack(() => data.initialCompare2Id || 'ply_gyokeres'));
	let playerComparison = $state<PlayerComparison | null>(
		untrack(() => data.initialPlayerComparison)
	);
	let squadError = $state<string | null>(untrack(() => data.initialSquadError ?? null));
	let squadLoading = $state(false);

	// Modal & toast state
	let isModalOpen = $state(false);
	let insightTitle = $state('');
	let insightDesc = $state('');
	let isSavingInsight = $state(false);
	let modalError = $state<{ message: string; isAuth?: boolean } | null>(null);
	let toastMessage = $state<string | null>(null);
	let toastKind = $state<'success' | 'error'>('success');
	let toastNeedsLogin = $state(false);
	let toastTimer: ReturnType<typeof setTimeout> | null = null;

	let lastSyncStamp = $state<string>(untrack(() => buildStamp(data)));
	let queryRequestSeq = 0;
	let trendsRequestSeq = 0;
	let h2hRequestSeq = 0;
	let squadRequestSeq = 0;

	$effect(() => {
		const stamp = buildStamp(data);
		if (stamp !== lastSyncStamp) {
			lastSyncStamp = stamp;
			activeTab = data.initialTab || 'query';
			mode = data.initialTeamIds.length > 1 ? 'comparison' : 'single';
			team1 = data.initialTeamIds[0] || 'arsenal';
			team2 = data.initialTeamIds[1] || 'real-madrid';
			metric = data.initialMetric || 'win_rate';
			venue = data.initialVenue || 'all';
			selectedSeason = data.activeSeasonId || 'all';
			result = data.initialResult;
			queryError = data.initialQueryError ?? null;
			resultSnapshotMeta = data.initialResult
				? {
						metric: data.initialMetric || 'win_rate',
						team_ids: data.initialTeamIds,
						venue: data.initialVenue || 'all',
						season_id: data.activeSeasonId || 'all'
					}
				: null;
			insights = data.insights || [];
			insightsError = data.insightsError ?? null;

			trendsClub = data.initialTrendsClub || 'arsenal';
			trendsVenue = data.initialVenue || 'all';
			trendMetric = data.initialTrendMetric || 'win_rate';
			trendsData = data.initialTrends;
			trendsError = data.initialTrendsError ?? null;
			selectedTrendSeasonId = pickInitialTrendSeasonId(data.initialTrends);

			h2hClub = data.initialH2HClub || 'arsenal';
			h2hOpponent = data.initialOpponentId || 'chelsea';
			h2hVenue = data.initialVenue || 'all';
			h2hData = data.initialH2H;
			h2hError = data.initialH2HError ?? null;

			comparePlayer1Id = data.initialCompare1Id || 'ply_saka';
			comparePlayer2Id = data.initialCompare2Id || 'ply_gyokeres';
			playerComparison = data.initialPlayerComparison;
			squadError = data.initialSquadError ?? null;
		}
	});

	let queryBtnLabel = $derived(loading ? 'Computing…' : 'Calculate analytics');
	let trendsBtnLabel = $derived(trendsLoading ? 'Updating trends…' : 'Refresh season curve');
	let h2hBtnLabel = $derived(h2hLoading ? 'Loading ledger…' : 'Load head-to-head');
	let squadBtnLabel = $derived(squadLoading ? 'Comparing players…' : 'Compare Arsenal players');
	let publishBtnLabel = $derived(isSavingInsight ? 'Publishing…' : 'Publish insight');
	let primaryClubLabel = $derived(mode === 'single' ? 'Club' : 'Club A');
	let visibleInsights = $derived(showAllInsights ? insights : insights.slice(0, 6));
	let trimmedInsightTitle = $derived(insightTitle.trim());
	let isInsightTitleValid = $derived(
		trimmedInsightTitle.length >= 3 && trimmedInsightTitle.length <= 200
	);

	const labTabs: Array<{ id: LabTab; label: string; hint: string }> = [
		{ id: 'query', label: 'Analytics query', hint: 'Single club or club-to-club metrics' },
		{ id: 'trends', label: 'Multi-season trends', hint: 'Arteta era 2019/20 to 2026/27' },
		{ id: 'h2h', label: 'Opponent H2H', hint: 'Club ledger & recent fixtures' },
		{ id: 'squad', label: 'Squad H2H', hint: 'Player per-90 & efficiency bars' },
		{ id: 'pitch', label: 'Classic matches & xG pitch', hint: 'StatsBomb 2D shot map & passes' }
	];

	const metricsList = [
		{ id: 'win_rate', label: 'Win rate (%)' },
		{ id: 'goals_per_match', label: 'Goals per match' },
		{ id: 'points_per_game', label: 'Points per game (PPG)' },
		{ id: 'goal_difference', label: 'Goal difference' },
		{ id: 'clean_sheet_rate', label: 'Clean sheet rate (%)' },
		{ id: 'loss_rate', label: 'Loss rate (%)' }
	];

	const trendMetrics: Array<{ id: TrendMetricKey; label: string; unit: string; maxBound: number }> = [
		{ id: 'win_rate', label: 'Win rate (%)', unit: '%', maxBound: 100 },
		{ id: 'points_per_game', label: 'Points per game (PPG)', unit: 'PPG', maxBound: 3 },
		{ id: 'goals_per_match', label: 'Goals per match', unit: 'G/M', maxBound: 4 },
		{ id: 'clean_sheet_rate', label: 'Clean sheet rate (%)', unit: '%', maxBound: 100 }
	];

	function syncUrlParams(updates: Record<string, string | null>) {
		if (typeof window === 'undefined') return;
		const url = new URL(window.location.href);
		for (const [k, v] of Object.entries(updates)) {
			if (v === null || v === '') {
				url.searchParams.delete(k);
			} else {
				url.searchParams.set(k, v);
			}
		}
		window.history.replaceState({}, '', url.toString());
	}

	function switchTab(nextTab: LabTab) {
		activeTab = nextTab;
		syncUrlParams({ tab: nextTab });
	}

	function handleTabKeydown(event: KeyboardEvent, currentIdx: number) {
		let nextIdx = -1;
		if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
			nextIdx = (currentIdx + 1) % labTabs.length;
		} else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
			nextIdx = (currentIdx - 1 + labTabs.length) % labTabs.length;
		} else if (event.key === 'Home') {
			nextIdx = 0;
		} else if (event.key === 'End') {
			nextIdx = labTabs.length - 1;
		}
		if (nextIdx !== -1) {
			event.preventDefault();
			const targetTab = labTabs[nextIdx];
			switchTab(targetTab.id);
			const el = document.getElementById(`tab-${targetTab.id}`);
			el?.focus();
		}
	}

	function updateUrlState(team_ids: string[]) {
		syncUrlParams({
			tab: activeTab,
			metric,
			teams: team_ids.join(','),
			venue,
			season: selectedSeason !== 'all' ? selectedSeason : null
		});
	}

	async function runQuery() {
		if (mode === 'comparison' && team1 === team2) {
			const alt = clubList.find((c) => c.id !== team1);
			if (alt) team2 = alt.id;
		}
		loading = true;
		queryError = null;
		const snapshotMetric = metric;
		const snapshotVenue = venue;
		const snapshotSeason = selectedSeason;
		const team_ids = mode === 'single' ? [team1] : [team1, team2];
		const reqId = ++queryRequestSeq;
		try {
			const res = await queryAnalyticsStrict({
				metric: snapshotMetric,
				team_ids,
				venue: snapshotVenue,
				season_id: snapshotSeason !== 'all' ? snapshotSeason : undefined
			});
			if (reqId !== queryRequestSeq) return;
			result = res;
			resultSnapshotMeta = {
				metric: snapshotMetric,
				team_ids,
				venue: snapshotVenue,
				season_id: snapshotSeason
			};
			updateUrlState(team_ids);
		} catch (err) {
			if (reqId !== queryRequestSeq) return;
			queryError =
				err instanceof ApiError
					? err.detail
					: 'Unable to reach Data Lab analytics engine right now.';
		} finally {
			if (reqId === queryRequestSeq) {
				loading = false;
			}
		}
	}

	async function runTrendsQuery() {
		trendsLoading = true;
		trendsError = null;
		const reqId = ++trendsRequestSeq;
		try {
			const res = await fetchMultiSeasonTrendsStrict(trendsClub, trendsVenue);
			if (reqId !== trendsRequestSeq) return;
			trendsData = res;
			if (res && res.trends.length > 0) {
				const valid = res.trends.filter((t) => t.matches_played > 0);
				const stillExists = res.trends.some((t) => t.season_id === selectedTrendSeasonId);
				if (!stillExists) {
					selectedTrendSeasonId =
						valid.length > 0 ? valid[valid.length - 1].season_id : res.trends[0].season_id;
				}
			}
			syncUrlParams({
				tab: 'trends',
				club: trendsClub,
				tmetric: trendMetric,
				venue: trendsVenue
			});
		} catch (err) {
			if (reqId !== trendsRequestSeq) return;
			trendsError =
				err instanceof ApiError
					? err.detail
					: 'Unable to load multi-season trajectories right now.';
		} finally {
			if (reqId === trendsRequestSeq) {
				trendsLoading = false;
			}
		}
	}

	async function runH2HQuery() {
		if (h2hClub === h2hOpponent) {
			const alt = h2hOpponentOptions.find((o) => o.opponent_id !== h2hClub);
			if (alt) h2hOpponent = alt.opponent_id;
		}
		h2hLoading = true;
		h2hError = null;
		const reqId = ++h2hRequestSeq;
		try {
			const res = await fetchOpponentH2HStrict(h2hOpponent, h2hClub, h2hVenue);
			if (reqId !== h2hRequestSeq) return;
			h2hData = res;
			syncUrlParams({
				tab: 'h2h',
				hclub: h2hClub,
				opponent: h2hOpponent,
				venue: h2hVenue
			});
		} catch (err) {
			if (reqId !== h2hRequestSeq) return;
			h2hError =
				err instanceof ApiError
					? err.detail
					: 'Unable to load opponent head-to-head records right now.';
		} finally {
			if (reqId === h2hRequestSeq) {
				h2hLoading = false;
			}
		}
	}

	async function runSquadComparison() {
		if (!comparePlayer1Id || !comparePlayer2Id || comparePlayer1Id === comparePlayer2Id) return;
		squadLoading = true;
		squadError = null;
		const reqId = ++squadRequestSeq;
		try {
			const res = await comparePlayersStrict(comparePlayer1Id, comparePlayer2Id);
			if (reqId !== squadRequestSeq) return;
			playerComparison = res;
			syncUrlParams({ tab: 'squad', p1: comparePlayer1Id, p2: comparePlayer2Id });
		} catch (err) {
			if (reqId !== squadRequestSeq) return;
			squadError =
				err instanceof ApiError
					? err.detail
					: 'Unable to compare selected Arsenal players right now.';
		} finally {
			if (reqId === squadRequestSeq) {
				squadLoading = false;
			}
		}
	}

	async function retryInsights() {
		isRetryingInsights = true;
		try {
			const res = await fetchInsightsResult();
			insightsError = res.error;
			if (!res.error) insights = res.data;
		} finally {
			isRetryingInsights = false;
		}
	}

	async function copyShareLink() {
		if (typeof window === 'undefined') return;
		try {
			await navigator.clipboard.writeText(window.location.href);
			showToast('Reproducible analysis link copied to clipboard.');
		} catch {
			showToast('Clipboard permission unavailable: copy the URL from your browser address bar.', 'error');
		}
	}

	function openCreateModal() {
		if (!result || result.series.length === 0) return;
		if (!data.user || !data.session?.access_token) {
			showToast('Please sign in to publish Data Lab insights.', 'error', true);
			return;
		}
		modalError = null;
		const snapMetric = result.metric || resultSnapshotMeta?.metric || metric;
		const snapVenue = result.venue_filter || resultSnapshotMeta?.venue || venue;
		const snapSeason = resultSnapshotMeta?.season_id || selectedSeason;
		const t1 = result.series[0];
		if (result.series.length === 1) {
			insightTitle = `${t1.team_name} ${getMetricLabel(snapMetric)}: ${t1.metric_value} ${t1.unit} (${snapVenue})`;
		} else {
			const t2 = result.series[1];
			insightTitle = `${t1.team_name} vs ${t2.team_name}: ${getMetricLabel(snapMetric)} comparison`;
		}
		const seasonNote =
			snapSeason && snapSeason !== 'all'
				? ` Season filter: ${seasons.find((s) => s.id === snapSeason)?.label || snapSeason}.`
				: '';
		insightDesc = `Computed across eligible completed matches (venue filter: ${snapVenue}).${seasonNote}`;
		isModalOpen = true;
	}

	async function submitInsight() {
		if (!result || !isInsightTitleValid) {
			modalError = { message: 'Insight title must be between 3 and 200 characters.' };
			return;
		}
		if (!data.user || !data.session?.access_token) {
			modalError = { message: 'Please sign in to publish Data Lab insights.', isAuth: true };
			showToast('Please sign in to publish Data Lab insights.', 'error', true);
			return;
		}
		modalError = null;
		isSavingInsight = true;
		try {
			const snapMetric = result.metric || resultSnapshotMeta?.metric || metric;
			const snapVenue = result.venue_filter || resultSnapshotMeta?.venue || venue;
			const snapTeams =
				result.series.length > 0
					? result.series.map((s) => s.team_id)
					: resultSnapshotMeta?.team_ids || (mode === 'single' ? [team1] : [team1, team2]);
			const newInsight = await createInsight(
				{
					title: trimmedInsightTitle,
					description: insightDesc.trim() || undefined,
					metric: snapMetric,
					team_ids: snapTeams,
					venue: snapVenue,
					chart_type: snapTeams.length === 1 ? 'bar' : 'comparison',
					author_name:
						data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter',
					author_club_id: data.profile?.favorite_club_id || 'arsenal',
					snapshot: result
				},
				data.session?.access_token
			);

			if (newInsight) {
				insights = [newInsight, ...insights];
				insightsError = null;
				isModalOpen = false;
				showToast('Insight published to the community feed.', 'success', false);
			}
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			const msg = isAuth
				? 'Please sign in to publish Data Lab insights.'
				: err instanceof ApiError
					? err.detail
					: 'Could not publish insight. Please try again.';
			modalError = { message: msg, isAuth };
			showToast(msg, 'error', isAuth);
		} finally {
			isSavingInsight = false;
		}
	}

	async function handleDeleteInsight(ins: Insight) {
		if (!data.session?.access_token) {
			showToast('Please sign in to manage your insights.', 'error', true);
			return;
		}
		deletingInsightId = ins.id;
		try {
			await deleteInsight(ins.id, data.session.access_token);
			insights = insights.filter((i) => i.id !== ins.id);
			confirmDeleteInsightId = null;
			showToast(`Deleted insight “${ins.title}”.`, 'success', false);
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			showToast(
				isAuth
					? 'Please sign in to delete this insight.'
					: err instanceof ApiError
						? err.detail
						: 'Could not delete insight. Please try again.',
				'error',
				isAuth
			);
		} finally {
			deletingInsightId = null;
		}
	}

	function loadExistingInsight(ins: Insight) {
		activeTab = 'query';
		metric = ins.metric;
		venue = ins.venue;
		selectedSeason = 'all';
		if (ins.team_ids.length > 1) {
			mode = 'comparison';
			team1 = ins.team_ids[0];
			team2 = ins.team_ids[1];
		} else {
			mode = 'single';
			team1 = ins.team_ids[0];
		}
		result = ins.snapshot;
		queryError = null;
		resultSnapshotMeta = {
			metric: ins.metric,
			team_ids: ins.team_ids,
			venue: ins.venue,
			season_id: 'all'
		};
		updateUrlState(ins.team_ids);
		showToast(`Loaded insight: “${ins.title}”`, 'success', false);
	}

	function getMetricLabel(id: string): string {
		return metricsList.find((m) => m.id === id)?.label || id;
	}

	function showToast(
		msg: string,
		kind: 'success' | 'error' = 'success',
		needsLogin: boolean = false
	) {
		if (toastTimer) clearTimeout(toastTimer);
		toastMessage = msg;
		toastKind = kind;
		toastNeedsLogin = needsLogin;
		toastTimer = setTimeout(() => {
			toastMessage = null;
			toastNeedsLogin = false;
		}, 5000);
	}

	function formatShortDate(isoStr: string): string {
		try {
			return new Date(isoStr).toLocaleDateString(undefined, {
				year: 'numeric',
				month: 'short',
				day: 'numeric'
			});
		} catch {
			return isoStr;
		}
	}

	// Lens 1 derived helpers
	let maxMetricVal = $derived(
		result && result.series.length > 0
			? Math.max(...result.series.map((s) => Math.abs(s.metric_value)), 1)
			: 1
	);

	let deltaDiff = $derived.by(() => {
		if (!result || result.series.length < 2) return null;
		const s1 = result.series[0];
		const s2 = result.series[1];
		if (s1.matches_played === 0 || s2.matches_played === 0) {
			return {
				leader: 'Incomplete sample',
				text: 'One or both clubs have 0 completed matches under this filter'
			};
		}
		const diff = Math.round((s1.metric_value - s2.metric_value) * 10) / 10;
		if (diff === 0) return { leader: 'Tied', text: 'Equal performance' };
		const leaderName = diff > 0 ? s1.team_name : s2.team_name;
		return {
			leader: leaderName,
			text: `${leaderName} leads by ${Math.abs(diff)} ${s1.unit}`
		};
	});

	// Lens 2 (Multi-season trends) SVG geometry
	const CHART_W = 720;
	const CHART_H = 300;
	const PAD_L = 52;
	const PAD_R = 24;
	const PAD_T = 24;
	const PAD_B = 42;
	const PLOT_W = CHART_W - PAD_L - PAD_R;
	const PLOT_H = CHART_H - PAD_T - PAD_B;

	let activeTrendMeta = $derived(
		trendMetrics.find((m) => m.id === trendMetric) || trendMetrics[0]
	);

	function getTrendValue(item: SeasonTrendItem, key: TrendMetricKey): number {
		return item[key] ?? 0;
	}

	function shortSeasonLabel(item: SeasonTrendItem): string {
		const sy = String(item.start_year).slice(-2);
		const ey = String(item.end_year).slice(-2);
		return `${sy}/${ey}`;
	}

	let trendScale = $derived.by(() => {
		const rows = trendsData?.trends || [];
		const meta = activeTrendMeta;
		let ceiling = meta.maxBound;
		if (trendMetric === 'goals_per_match') {
			const highest = Math.max(
				2.5,
				...rows.map((r) => (r.matches_played > 0 ? r.goals_per_match : 0))
			);
			ceiling = Math.ceil(highest * 2) / 2;
		}
		const ticks = [0, ceiling * 0.25, ceiling * 0.5, ceiling * 0.75, ceiling];
		const points = rows.map((row, idx) => {
			const count = Math.max(rows.length - 1, 1);
			const x = rows.length === 1 ? PAD_L + PLOT_W / 2 : PAD_L + (idx / count) * PLOT_W;
			const val = getTrendValue(row, trendMetric);
			const clamped = Math.max(0, Math.min(ceiling, val));
			const y = PAD_T + PLOT_H - (clamped / ceiling) * PLOT_H;
			return { row, x, y, val, hasData: row.matches_played > 0 };
		});

		const baselineY = PAD_T + PLOT_H;

		// Break paths cleanly across unplayed intermediate seasons instead of fabricating continuity
		const runs: Array<typeof points> = [];
		let currentRun: typeof points = [];
		for (const pt of points) {
			if (pt.hasData) {
				currentRun.push(pt);
			} else if (currentRun.length > 0) {
				runs.push(currentRun);
				currentRun = [];
			}
		}
		if (currentRun.length > 0) runs.push(currentRun);

		const linePath = runs
			.filter((r) => r.length > 1)
			.map((r) =>
				r.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
			)
			.join(' ');

		const areaPaths = runs
			.filter((r) => r.length > 1)
			.map((r) => {
				const seg = r
					.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
					.join(' ');
				return `${seg} L ${r[r.length - 1].x.toFixed(1)} ${baselineY} L ${r[0].x.toFixed(1)} ${baselineY} Z`;
			});

		return { ceiling, ticks, points, linePath, areaPaths, baselineY };
	});

	let activeTrendItem = $derived.by(() => {
		const rows = trendsData?.trends || [];
		if (rows.length === 0) return null;
		return (
			rows.find((r) => r.season_id === selectedTrendSeasonId) ||
			rows.find((r) => r.matches_played > 0) ||
			rows[0]
		);
	});

	function handleTrendPointKeydown(event: KeyboardEvent, seasonId: string) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			selectedTrendSeasonId = seasonId;
		}
	}

	// Lens 3 (Opponent H2H) helpers
	let h2hOpponentOptions = $derived.by(() => {
		if (h2hData?.available_opponents && h2hData.available_opponents.length > 0) {
			return h2hData.available_opponents;
		}
		return [
			{ opponent_id: 'chelsea', opponent_name: 'Chelsea FC', matches_played: 0 },
			{ opponent_id: 'real-madrid', opponent_name: 'Real Madrid CF', matches_played: 0 },
			{ opponent_id: 'barcelona', opponent_name: 'FC Barcelona', matches_played: 0 },
			{ opponent_id: 'milan', opponent_name: 'AC Milan', matches_played: 0 }
		];
	});

	function getH2HMatchOutcome(
		homeId: string,
		awayId: string,
		homeScore: number | undefined,
		awayScore: number | undefined,
		perspectiveClubId: string
	): 'W' | 'D' | 'L' {
		if (homeScore === undefined || awayScore === undefined) return 'D';
		if (homeScore === awayScore) return 'D';
		const isHome = homeId === perspectiveClubId;
		const won = isHome ? homeScore > awayScore : awayScore > homeScore;
		return won ? 'W' : 'L';
	}

	// Lens 4 (Squad H2H) normalized metric bars
	let squadComparisonBars = $derived.by(() => {
		if (!playerComparison) return [];
		const a = playerComparison.player1;
		const b = playerComparison.player2;

		const maxG90 = Math.max(a.goals_per_90, b.goals_per_90, 0.01);
		const maxA90 = Math.max(a.assists_per_90, b.assists_per_90, 0.01);
		const minMpc = Math.min(a.minutes_per_contribution, b.minutes_per_contribution);
		const aMpcPct =
			a.minutes_per_contribution > 0 ? (minMpc / a.minutes_per_contribution) * 100 : 0;
		const bMpcPct =
			b.minutes_per_contribution > 0 ? (minMpc / b.minutes_per_contribution) * 100 : 0;
		const maxContrib = Math.max(a.player.goal_contributions, b.player.goal_contributions, 1);

		return [
			{
				key: 'goals_per_90',
				label: 'Goals per 90 min',
				note: 'Higher bar reflects greater scoring rate per 90 minutes.',
				p1Text: a.goals_per_90.toFixed(2),
				p2Text: b.goals_per_90.toFixed(2),
				p1Pct: (a.goals_per_90 / maxG90) * 100,
				p2Pct: (b.goals_per_90 / maxG90) * 100
			},
			{
				key: 'assists_per_90',
				label: 'Assists per 90 min',
				note: 'Higher bar reflects greater chance creation output per 90 minutes.',
				p1Text: a.assists_per_90.toFixed(2),
				p2Text: b.assists_per_90.toFixed(2),
				p1Pct: (a.assists_per_90 / maxA90) * 100,
				p2Pct: (b.assists_per_90 / maxA90) * 100
			},
			{
				key: 'minutes_per_contribution',
				label: 'Minutes per G+A contribution',
				note: 'Lower minutes per contribution is faster; bar scales inversely to highlight efficiency.',
				p1Text: `${a.minutes_per_contribution.toFixed(1)} min`,
				p2Text: `${b.minutes_per_contribution.toFixed(1)} min`,
				p1Pct: aMpcPct,
				p2Pct: bMpcPct
			},
			{
				key: 'discipline_score',
				label: 'Discipline score',
				note: 'Out of 10.0, deducting 0.5 per yellow card and 2.0 per red card.',
				p1Text: `${a.discipline_score.toFixed(1)} / 10`,
				p2Text: `${b.discipline_score.toFixed(1)} / 10`,
				p1Pct: Math.max(0, Math.min(100, (a.discipline_score / 10) * 100)),
				p2Pct: Math.max(0, Math.min(100, (b.discipline_score / 10) * 100))
			},
			{
				key: 'goal_contributions',
				label: 'Total goal contributions (G+A)',
				note: 'Combined goals and assists across current campaign appearances.',
				p1Text: `${a.player.goal_contributions} (${a.player.goals}G, ${a.player.assists}A)`,
				p2Text: `${b.player.goal_contributions} (${b.player.goals}G, ${b.player.assists}A)`,
				p1Pct: (a.player.goal_contributions / maxContrib) * 100,
				p2Pct: (b.player.goal_contributions / maxContrib) * 100
			}
		];
	});
</script>

<svelte:head>
	<title>The Data Lab | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-10">
	<!-- Toast Notification -->
	{#if toastMessage}
		<div
			role={toastKind === 'error' ? 'alert' : 'status'}
			class="fixed bottom-6 right-6 left-6 sm:left-auto max-w-md z-[var(--z-toast)] bg-paper-2 border border-rule-2 px-4 py-3 rounded-card text-xs flex items-center justify-between gap-3 {toastKind === 'error' ? 'text-error' : 'text-success'}"
		>
			<div class="flex items-center gap-3 flex-wrap min-w-0">
				<span>{toastMessage}</span>
				{#if toastNeedsLogin}
					<a href="/login?next=/lab" class="underline text-ink font-semibold hover:text-accent-text">
						Sign in
					</a>
				{/if}
			</div>
			<button
				type="button"
				onclick={() => (toastMessage = null)}
				class="min-h-[44px] px-2 text-muted hover:text-ink font-semibold shrink-0"
			>
				Close
			</button>
		</div>
	{/if}

	<!-- Editorial Header -->
	<div class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-2 border-rule-2 pb-8">
		<div class="space-y-3">
			<h1>The Data Lab</h1>
			<p class="lead text-ink-2">
				Reproducible Mikel Arteta era analytics, multi-season trajectories, opponent ledgers, squad comparisons, and StatsBomb event telemetry.
			</p>
		</div>

		<div class="flex items-center gap-3 flex-wrap">
			<a
				href="/lab/historical"
				class="min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs text-accent-2 font-semibold transition-colors inline-flex items-center whitespace-nowrap"
			>
				StatsBomb 2D pitch
			</a>
			<span class="text-xs text-muted">
				Coverage: Arteta era (<span class="num font-outlier">2019</span> to present)
			</span>
		</div>
	</div>

	<!-- 2-Column Workbench -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
		<!-- Left Workbench Control Column (4 cols) -->
		<aside class="lg:col-span-4 space-y-6 bg-paper-2 border-t-2 border-rule-2 p-5">
			<!-- Lens Switcher -->
			<div class="space-y-2">
				<div class="text-xs font-semibold text-muted pb-1">Analytical lens</div>
				<div
					role="tablist"
					aria-label="Data Lab analytical lenses"
					aria-orientation="vertical"
					class="divide-y divide-rule border-y border-rule"
				>
					{#each labTabs as tab, idx (tab.id)}
						{@const isActive = activeTab === tab.id}
						<button
							id="tab-{tab.id}"
							type="button"
							role="tab"
							aria-selected={isActive}
							aria-controls="lab-tabpanel"
							tabindex={isActive ? 0 : -1}
							onclick={() => switchTab(tab.id)}
							onkeydown={(e) => handleTabKeydown(e, idx)}
							class="w-full min-h-[44px] py-2.5 px-3 text-left flex items-center justify-between gap-2 transition-colors {isActive ? 'bg-paper-3 text-ink border border-rule-2' : 'text-ink-2 hover:text-ink hover:bg-paper-3'}"
						>
							<span class="text-sm font-semibold">{tab.label}</span>
							<span class="text-xs text-muted truncate max-w-[140px]">{tab.hint}</span>
						</button>
					{/each}
				</div>
			</div>

			<!-- Tab-Specific Controls -->
			<div class="border-t border-rule pt-5 space-y-4">
				{#if activeTab === 'query'}
					<div class="space-y-4">
						<div class="grid grid-cols-2 gap-2 text-xs">
							<button
								type="button"
								onclick={() => { mode = 'single'; runQuery(); }}
								aria-pressed={mode === 'single'}
								class="min-h-[44px] px-3 rounded-card transition-colors font-semibold border {mode === 'single' ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper text-ink-2 border-rule hover:text-ink'}"
							>
								Single club analysis
							</button>
							<button
								type="button"
								onclick={() => { mode = 'comparison'; runQuery(); }}
								aria-pressed={mode === 'comparison'}
								class="min-h-[44px] px-3 rounded-card transition-colors font-semibold border {mode === 'comparison' ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper text-ink-2 border-rule hover:text-ink'}"
							>
								Head-to-head comparison
							</button>
						</div>

						<div>
							<label for="primary-club" class="block text-xs font-semibold text-ink-2 mb-1.5">
								{primaryClubLabel}
							</label>
							<select
								id="primary-club"
								bind:value={team1}
								onchange={runQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each clubList as club (club.id)}
									<option value={club.id}>{club.name}</option>
								{/each}
							</select>
						</div>

						{#if mode === 'comparison'}
							<div>
								<label for="secondary-club" class="block text-xs font-semibold text-ink-2 mb-1.5">
									Club B (compare)
								</label>
								<select
									id="secondary-club"
									bind:value={team2}
									onchange={runQuery}
									class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
								>
									{#each clubList as club (club.id)}
										<option value={club.id} disabled={club.id === team1}>{club.name}</option>
									{/each}
								</select>
							</div>
						{/if}

						<div>
							<label for="metric-select" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Metric
							</label>
							<select
								id="metric-select"
								bind:value={metric}
								onchange={runQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each metricsList as m (m.id)}
									<option value={m.id}>{m.label}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="venue-filter" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Venue filter
							</label>
							<select
								id="venue-filter"
								bind:value={venue}
								onchange={runQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								<option value="all">All matches</option>
								<option value="home">Home matches only</option>
								<option value="away">Away matches only</option>
							</select>
						</div>

						<div>
							<label for="season-filter" class="block text-xs font-semibold text-accent-2 mb-1.5">
								Arteta season
							</label>
							<select
								id="season-filter"
								bind:value={selectedSeason}
								onchange={runQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-accent-2 num font-outlier"
							>
								<option value="all">All (2019 to present)</option>
								{#each seasons as s (s.id)}
									<option value={s.id}>{s.label}</option>
								{/each}
							</select>
						</div>

						<button
							type="button"
							onclick={runQuery}
							disabled={loading}
							class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 disabled:opacity-60 text-accent-ink font-semibold text-xs rounded-card transition-opacity"
						>
							{queryBtnLabel}
						</button>
					</div>
				{:else if activeTab === 'trends'}
					<div class="space-y-4">
						<div>
							<label for="trends-club" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Club timeline
							</label>
							<select
								id="trends-club"
								bind:value={trendsClub}
								onchange={runTrendsQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each clubList as club (club.id)}
									<option value={club.id}>{club.name}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="trends-metric" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Trajectory metric
							</label>
							<select
								id="trends-metric"
								bind:value={trendMetric}
								onchange={() => syncUrlParams({ tab: 'trends', tmetric: trendMetric, club: trendsClub, venue: trendsVenue })}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each trendMetrics as tm (tm.id)}
									<option value={tm.id}>{tm.label}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="trends-venue" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Venue filter
							</label>
							<select
								id="trends-venue"
								bind:value={trendsVenue}
								onchange={runTrendsQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								<option value="all">All venues</option>
								<option value="home">Home matches only</option>
								<option value="away">Away matches only</option>
							</select>
						</div>

						<button
							type="button"
							onclick={runTrendsQuery}
							disabled={trendsLoading}
							class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 disabled:opacity-60 text-accent-ink font-semibold text-xs rounded-card transition-opacity whitespace-nowrap"
						>
							{trendsBtnLabel}
						</button>
					</div>
				{:else if activeTab === 'h2h'}
					<div class="space-y-4">
						<div>
							<label for="h2h-club" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Primary club
							</label>
							<select
								id="h2h-club"
								bind:value={h2hClub}
								onchange={runH2HQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each clubList as club (club.id)}
									<option value={club.id}>{club.name}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="h2h-opponent" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Opponent
							</label>
							<select
								id="h2h-opponent"
								bind:value={h2hOpponent}
								onchange={runH2HQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each h2hOpponentOptions as opt (opt.opponent_id)}
									<option value={opt.opponent_id} disabled={opt.opponent_id === h2hClub}>
										{opt.opponent_name} ({opt.matches_played})
									</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="h2h-venue" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Venue filter
							</label>
							<select
								id="h2h-venue"
								bind:value={h2hVenue}
								onchange={runH2HQuery}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								<option value="all">All venues</option>
								<option value="home">Home matches only</option>
								<option value="away">Away matches only</option>
							</select>
						</div>

						<button
							type="button"
							onclick={runH2HQuery}
							disabled={h2hLoading}
							class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 disabled:opacity-60 text-accent-ink font-semibold text-xs rounded-card transition-opacity whitespace-nowrap"
						>
							{h2hBtnLabel}
						</button>
					</div>
				{:else if activeTab === 'squad'}
					<div class="space-y-4">
						<div>
							<label for="squad-player-1" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Player A
							</label>
							<select
								id="squad-player-1"
								bind:value={comparePlayer1Id}
								onchange={runSquadComparison}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each squadList as p (p.id)}
									<option value={p.id} disabled={p.id === comparePlayer2Id}>
										#{p.jersey_number} {p.name} ({p.position})
									</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="squad-player-2" class="block text-xs font-semibold text-ink-2 mb-1.5">
								Player B
							</label>
							<select
								id="squad-player-2"
								bind:value={comparePlayer2Id}
								onchange={runSquadComparison}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
							>
								{#each squadList as p (p.id)}
									<option value={p.id} disabled={p.id === comparePlayer1Id}>
										#{p.jersey_number} {p.name} ({p.position})
									</option>
								{/each}
							</select>
						</div>

						<button
							type="button"
							onclick={runSquadComparison}
							disabled={squadLoading || comparePlayer1Id === comparePlayer2Id}
							class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 disabled:opacity-50 text-accent-ink font-semibold text-xs rounded-card transition-opacity whitespace-nowrap"
						>
							{squadBtnLabel}
						</button>
					</div>
				{:else}
					<div class="space-y-3 text-xs text-ink-2">
						<p class="leading-relaxed">
							Inspect coordinate-level xG shot maps and average positional passing networks from classic Arsenal matches directly inside the workbench.
						</p>
						<a
							href="/lab/historical"
							class="inline-flex items-center justify-center w-full min-h-[44px] px-3 rounded-card border border-rule bg-paper hover:bg-paper-3 text-xs font-semibold text-ink transition-colors"
						>
							Open standalone pitch view
						</a>
					</div>
				{/if}
			</div>

			<!-- Action Bar -->
			<div class="border-t border-rule pt-4 flex flex-col gap-2.5">
				<button
					type="button"
					onclick={copyShareLink}
					class="w-full min-h-[44px] px-4 rounded-card border border-rule bg-paper hover:bg-paper-3 text-xs text-ink-2 hover:text-ink font-semibold transition-colors"
				>
					Share analysis link
				</button>
				{#if activeTab === 'query' && result && result.series.length > 0}
					<button
						type="button"
						onclick={openCreateModal}
						class="w-full min-h-[44px] px-4 rounded-card border border-rule-2 bg-paper-3 hover:bg-paper text-xs text-ink font-semibold transition-colors"
					>
						Save as insight
					</button>
				{/if}
			</div>

			<!-- Saved Insights Quick-Loader List -->
			<div class="border-t border-rule pt-5 space-y-3">
				<div class="flex items-baseline justify-between">
					<h2 class="text-sm font-bold text-ink">Saved insights</h2>
					<span class="text-xs text-muted num font-outlier">{insights.length}</span>
				</div>

				{#if insightsError && insights.length === 0}
					<StateBanner
						variant="error"
						title="Unable to load saved insights"
						message={insightsError}
						onretry={retryInsights}
						busy={isRetryingInsights}
					/>
				{:else if insights.length === 0}
					<p class="text-xs text-muted">
						No community insights saved yet. Run a query and publish the first snapshot.
					</p>
				{:else}
					<div class="divide-y divide-rule border-t border-rule">
						{#each visibleInsights as ins (ins.id)}
							{@const isOwner = Boolean(data.user?.id && ins.user_id && data.user.id === ins.user_id)}
							<div class="py-3 space-y-1.5">
								<div class="flex items-center justify-between gap-2 text-xs text-muted">
									<span class="text-accent-2 font-semibold">{getMetricLabel(ins.metric)}</span>
									<span class="num font-outlier">{formatShortDate(ins.created_at)}</span>
								</div>
								<div class="text-xs font-semibold text-ink leading-snug line-clamp-2">{ins.title}</div>
								<div class="flex items-center justify-between gap-2 text-xs pt-0.5 flex-wrap">
									<span class="text-muted">By {ins.author_name}</span>
									<div class="flex items-center gap-2">
										{#if isOwner}
											{#if confirmDeleteInsightId === ins.id}
												{@const delInsLabel = deletingInsightId === ins.id ? 'Deleting…' : 'Confirm'}
												<button
													type="button"
													disabled={deletingInsightId === ins.id}
													onclick={() => handleDeleteInsight(ins)}
													class="min-h-[44px] px-2 font-semibold text-error hover:text-ink whitespace-nowrap"
												>
													{delInsLabel}
												</button>
												<button
													type="button"
													onclick={() => (confirmDeleteInsightId = null)}
													class="min-h-[44px] px-1.5 text-muted hover:text-ink"
												>
													Cancel
												</button>
											{:else}
												<button
													type="button"
													onclick={() => (confirmDeleteInsightId = ins.id)}
													aria-label="Delete insight {ins.title}"
													class="min-h-[44px] px-2 font-semibold text-muted hover:text-error"
												>
													Delete
												</button>
											{/if}
										{/if}
										<button
											type="button"
											onclick={() => loadExistingInsight(ins)}
											class="min-h-[44px] px-2 font-semibold text-accent-text hover:underline"
										>
											Load
										</button>
									</div>
								</div>
							</div>
						{/each}
					</div>

					{#if insights.length > 6}
						{@const toggleInsLabel = showAllInsights ? 'Show fewer insights' : `Show all (${insights.length})`}
						<button
							type="button"
							onclick={() => (showAllInsights = !showAllInsights)}
							class="w-full min-h-[44px] text-xs font-semibold text-ink-2 hover:text-ink border border-rule rounded-card bg-paper hover:bg-paper-3 transition-colors whitespace-nowrap"
						>
							{toggleInsLabel}
						</button>
					{/if}
				{/if}
			</div>
		</aside>

		<!-- Right Analysis Stage (8 cols) -->
		<main class="lg:col-span-8 min-w-0">
			<div
				id="lab-tabpanel"
				role="tabpanel"
				aria-labelledby="tab-{activeTab}"
				class="space-y-8"
			>
			{#if activeTab === 'query'}
				{#if loading}
					<div class="py-16 border-t border-rule text-muted text-sm" role="status" aria-live="polite">
						Computing verified analytics across eligible completed records…
					</div>
				{:else if queryError}
					<StateBanner
						variant="error"
						title="Analytics query unavailable"
						message={queryError}
						onretry={runQuery}
						busy={loading}
					/>
				{:else if result && result.series.length > 0}
					{#if mode === 'single'}
						{@const s = result.series[0]}
						<div class="space-y-8">
							{#if s.team_id !== 'arsenal'}
								<StateBanner
									variant="info"
									title="Arsenal-fixture sample scope"
									message={`Metrics for ${s.team_name} are computed across stored fixtures involving Arsenal FC.`}
								/>
							{/if}

							<div class="grid grid-cols-1 md:grid-cols-12 gap-8">
								<!-- Big Metric Hero -->
								<div class="md:col-span-5 bg-paper-2 border-t-2 border-rule-2 p-6 flex flex-col justify-between space-y-6">
									<div class="space-y-2">
										<div class="flex items-center justify-between gap-2 flex-wrap">
											<span class="text-xs font-semibold text-ink-2">{s.team_name}</span>
											{#if s.matches_played > 0 && s.matches_played < 5}
												<span class="text-xs font-semibold text-accent-2 border border-rule px-2 py-0.5 rounded-card">
													Small sample (n = {s.matches_played})
												</span>
											{/if}
										</div>
										<div class="text-4xl font-bold text-ink num font-outlier">
											{#if s.matches_played === 0}
												n/a <span class="text-sm text-muted font-normal block mt-1">No completed matches in sample</span>
											{:else}
												{s.metric_value} <span class="text-lg text-accent-2 font-normal">{s.unit}</span>
											{/if}
										</div>
										<p class="text-xs text-muted">Formula: {result.formula}</p>
									</div>

									<!-- Visual Record Bar -->
									<div class="pt-4 border-t border-rule space-y-2">
										<div class="flex items-center justify-between text-xs text-ink-2">
											<span>Sample: <strong class="text-ink num font-outlier">{s.matches_played}</strong> matches</span>
											<div class="flex gap-3 num font-outlier font-semibold">
												<span class="text-success">{s.wins}W</span>
												<span class="text-accent-2">{s.draws}D</span>
												<span class="text-error">{s.losses}L</span>
											</div>
										</div>
										{#if s.matches_played > 0}
											<div class="w-full h-2 rounded-card bg-paper overflow-hidden flex">
												<div class="bg-success" style="width: {(s.wins / s.matches_played) * 100}%;" title="Wins"></div>
												<div class="bg-accent-2" style="width: {(s.draws / s.matches_played) * 100}%;" title="Draws"></div>
												<div class="bg-error" style="width: {(s.losses / s.matches_played) * 100}%;" title="Losses"></div>
											</div>
										{/if}
									</div>
								</div>

								<!-- Statistical Breakdown -->
								<div class="md:col-span-7 border-t-2 border-rule-2 pt-5 flex flex-col justify-between space-y-6">
									<div class="space-y-4">
										<h2 class="text-xl font-bold text-ink">Performance breakdown</h2>
										<div class="grid grid-cols-2 sm:grid-cols-4 gap-6 border-t border-rule pt-4">
											<div>
												<span class="text-xs text-muted">Goals for</span>
												<div class="text-2xl font-bold text-ink mt-1 num font-outlier">{s.goals_for}</div>
											</div>
											<div>
												<span class="text-xs text-muted">Goals against</span>
												<div class="text-2xl font-bold text-ink mt-1 num font-outlier">{s.goals_against}</div>
											</div>
											<div>
												<span class="text-xs text-muted">Goal diff</span>
												<div class="text-2xl font-bold mt-1 num font-outlier {s.goal_difference >= 0 ? 'text-success' : 'text-error'}">
													{s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference}
												</div>
											</div>
											<div>
												<span class="text-xs text-muted">Clean sheets</span>
												<div class="text-2xl font-bold text-ink mt-1 num font-outlier">{s.clean_sheets || 0}</div>
											</div>
										</div>
									</div>

									<div class="pt-4 border-t border-rule text-xs text-muted flex flex-col sm:flex-row sm:items-center justify-between gap-2">
										<span>{result.disclaimer}</span>
										<span>Venue filter: <strong class="text-ink-2">{result.venue_filter}</strong></span>
									</div>
								</div>
							</div>
						</div>
					{:else}
						<!-- Head-to-Head Comparison View -->
						{@const t1 = result.series[0]}
						{@const t2 = result.series[1]}

						<div class="space-y-8">
							{#if deltaDiff}
								<div class="border-y border-rule py-4 flex items-center justify-between flex-wrap gap-2 text-xs">
									<div class="flex items-center gap-2 flex-wrap">
										<span class="text-muted">Result:</span>
										<span class="text-sm font-bold text-accent-2">{deltaDiff.text}</span>
										{#if Math.abs(t1.matches_played - t2.matches_played) >= 10}
											<span class="text-xs text-ink-2 border border-rule px-2 py-0.5 rounded-card">
												Unequal sample sizes ({t1.matches_played} vs {t2.matches_played})
											</span>
										{/if}
									</div>
									<div class="text-muted">
										Comparing <strong class="text-ink">{t1.team_name}</strong> vs <strong class="text-ink">{t2.team_name}</strong> ({result.venue_filter} matches)
									</div>
								</div>
							{/if}

							<!-- Side-by-Side Stat Blocks -->
							<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
								<div class="bg-paper-2 border-t-2 border-rule-2 p-5 space-y-4">
									<div class="flex items-center justify-between gap-2">
										<h3 class="text-base font-bold text-ink card-headline">{t1.team_name}</h3>
										<span class="text-xs num font-outlier text-muted">{t1.matches_played} matches</span>
									</div>
									<div class="text-3xl font-bold num font-outlier text-ink">
										{#if t1.matches_played === 0}
											n/a <span class="text-xs text-muted font-normal">No matches</span>
										{:else}
											{t1.metric_value} <span class="text-base text-accent-2">{t1.unit}</span>
										{/if}
									</div>
									{#if t1.matches_played > 0 && t1.matches_played < 5}
										<p class="text-xs text-accent-2">Small sample (n = {t1.matches_played})</p>
									{/if}
									<div class="w-full bg-paper h-2.5 rounded-card overflow-hidden">
										<div
											class="h-full bg-accent"
											style="width: {t1.matches_played > 0 ? (Math.abs(t1.metric_value) / maxMetricVal) * 100 : 0}%;"
										></div>
									</div>
								</div>

								<div class="bg-paper-2 border-t-2 border-rule-2 p-5 space-y-4">
									<div class="flex items-center justify-between gap-2">
										<h3 class="text-base font-bold text-ink card-headline">{t2.team_name}</h3>
										<span class="text-xs num font-outlier text-muted">{t2.matches_played} matches</span>
									</div>
									<div class="text-3xl font-bold num font-outlier text-ink">
										{#if t2.matches_played === 0}
											n/a <span class="text-xs text-muted font-normal">No matches</span>
										{:else}
											{t2.metric_value} <span class="text-base text-accent-2">{t2.unit}</span>
										{/if}
									</div>
									{#if t2.matches_played > 0 && t2.matches_played < 5}
										<p class="text-xs text-accent-2">Small sample (n = {t2.matches_played})</p>
									{/if}
									<div class="w-full bg-paper h-2.5 rounded-card overflow-hidden">
										<div
											class="h-full bg-accent-2"
											style="width: {t2.matches_played > 0 ? (Math.abs(t2.metric_value) / maxMetricVal) * 100 : 0}%;"
										></div>
									</div>
								</div>
							</div>

							<!-- Comparison Breakdown Table -->
							<div class="overflow-x-auto border-t border-rule">
								<table class="w-full text-xs text-left">
									<thead class="text-muted border-b border-rule">
										<tr>
											<th class="py-3 pr-4 font-semibold">Statistical metric</th>
											<th class="py-3 px-4 font-bold text-ink">{t1.team_name}</th>
											<th class="py-3 pl-4 font-bold text-ink">{t2.team_name}</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-rule text-ink-2 num font-outlier">
										<tr>
											<td class="py-3 pr-4 font-body text-muted">Wins / draws / losses</td>
											<td class="py-3 px-4">{t1.wins}W / {t1.draws}D / {t1.losses}L</td>
											<td class="py-3 pl-4">{t2.wins}W / {t2.draws}D / {t2.losses}L</td>
										</tr>
										<tr>
											<td class="py-3 pr-4 font-body text-muted">Goals for / goals against</td>
											<td class="py-3 px-4">{t1.goals_for} GF / {t1.goals_against} GA</td>
											<td class="py-3 pl-4">{t2.goals_for} GF / {t2.goals_against} GA</td>
										</tr>
										<tr>
											<td class="py-3 pr-4 font-body text-muted">Goal difference</td>
											<td class="py-3 px-4 font-bold {t1.goal_difference >= 0 ? 'text-success' : 'text-error'}">
												{t1.goal_difference > 0 ? `+${t1.goal_difference}` : t1.goal_difference}
											</td>
											<td class="py-3 pl-4 font-bold {t2.goal_difference >= 0 ? 'text-success' : 'text-error'}">
												{t2.goal_difference > 0 ? `+${t2.goal_difference}` : t2.goal_difference}
											</td>
										</tr>
										<tr>
											<td class="py-3 pr-4 font-body text-muted">Clean sheets</td>
											<td class="py-3 px-4">{t1.clean_sheets || 0}</td>
											<td class="py-3 pl-4">{t2.clean_sheets || 0}</td>
										</tr>
										<tr>
											<td class="py-3 pr-4 font-body text-ink font-semibold">Selected metric ({getMetricLabel(result.metric || metric)})</td>
											<td class="py-3 px-4 font-bold text-accent-2">{t1.matches_played === 0 ? '—' : `${t1.metric_value} ${t1.unit}`}</td>
											<td class="py-3 pl-4 font-bold text-accent-2">{t2.matches_played === 0 ? '—' : `${t2.metric_value} ${t2.unit}`}</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
					{/if}
				{:else}
					<div class="py-12 border-t border-rule text-muted text-sm">
						No completed matches found matching the specified parameters.
					</div>
				{/if}

			{:else if activeTab === 'trends'}
				{#if trendsLoading}
					<div class="py-16 border-t border-rule text-muted text-sm" role="status" aria-live="polite">
						Compiling Mikel Arteta era seasonal trajectories…
					</div>
				{:else if trendsError}
					<StateBanner
						variant="error"
						title="Multi-season trends unavailable"
						message={trendsError}
						onretry={runTrendsQuery}
						busy={trendsLoading}
					/>
				{:else if trendsData && trendsData.trends.length > 0}
					<div class="space-y-8">
						<!-- Trends Header & Selected Point Callout -->
						<div class="border-t-2 border-rule-2 pt-5 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
							<div class="space-y-1 min-w-0">
								<h2 class="text-xl font-bold text-ink wrap-heading">
									{trendsData.club_name} multi-season trajectory ({activeTrendMeta.label})
								</h2>
								<p class="text-xs text-muted">
									Chronological progression across {trendsData.venue_filter} venues{trendsData.club_id !== 'arsenal' ? ' (Arsenal fixtures only)' : ''}. Select any season point or pill to inspect.
								</p>
							</div>
							{#if activeTrendItem}
								<div class="bg-paper-2 border border-rule px-4 py-2.5 rounded-card text-right shrink-0">
									<div class="text-xs text-muted">{activeTrendItem.label}</div>
									<div class="text-xl font-bold text-ink num font-outlier">
										{activeTrendItem.matches_played > 0
											? `${getTrendValue(activeTrendItem, trendMetric)} ${activeTrendMeta.unit}`
											: 'No matches'}
									</div>
									<div class="text-xs text-muted num font-outlier">
										{activeTrendItem.matches_played} matches
									</div>
								</div>
							{/if}
						</div>

						<!-- Interactive SVG Line & Point Chart (horizontally scrollable on small phones for readability) -->
						<div class="bg-paper-2 border-y border-rule p-5 space-y-4">
							<div class="overflow-x-auto">
								<div class="min-w-[540px]">
									<svg
										viewBox={`0 0 ${CHART_W} ${CHART_H}`}
										role="img"
										aria-label={`${trendsData.club_name} ${activeTrendMeta.label} trend from 2019/20 to 2026/27`}
										class="w-full h-auto block"
									>
										<defs>
											<linearGradient id="trend-area-grad" x1="0" y1="0" x2="0" y2="1">
												<stop offset="0%" stop-color="var(--color-accent)" stop-opacity="0.2" />
												<stop offset="100%" stop-color="var(--color-accent)" stop-opacity="0" />
											</linearGradient>
										</defs>

										<!-- Horizontal Gridlines & Y-Axis Ticks -->
										{#each trendScale.ticks as tickVal (tickVal)}
											{@const yPos = PAD_T + PLOT_H - (tickVal / trendScale.ceiling) * PLOT_H}
											<line
												x1={PAD_L}
												y1={yPos}
												x2={CHART_W - PAD_R}
												y2={yPos}
												stroke="var(--color-rule)"
												stroke-width="1"
											/>
											<text
												x={PAD_L - 10}
												y={yPos + 4}
												text-anchor="end"
												fill="var(--color-muted)"
												font-size="11"
												font-family="var(--font-outlier)"
											>
												{trendMetric === 'win_rate' || trendMetric === 'clean_sheet_rate'
													? `${Math.round(tickVal)}%`
													: tickVal.toFixed(1)}
											</text>
										{/each}

										<!-- Area Fills (split across unplayed season gaps) -->
										{#each trendScale.areaPaths as aPath, idx (`area_${idx}`)}
											<path d={aPath} fill="url(#trend-area-grad)" />
										{/each}

										<!-- Trend Line -->
										{#if trendScale.linePath}
											<path
												d={trendScale.linePath}
												fill="none"
												stroke="var(--color-accent)"
												stroke-width="2.5"
												stroke-linejoin="round"
												stroke-linecap="round"
											/>
										{/if}

										<!-- Season Points & X-Axis Labels -->
										{#each trendScale.points as pt (pt.row.season_id)}
											{@const isFocused = activeTrendItem?.season_id === pt.row.season_id}
											{@const shortLabel = shortSeasonLabel(pt.row)}
											<text
												x={pt.x}
												y={CHART_H - 14}
												text-anchor="middle"
												fill={isFocused ? 'var(--color-ink)' : 'var(--color-muted)'}
												font-size="11"
												font-weight={isFocused ? '700' : '400'}
												font-family="var(--font-outlier)"
											>
												{shortLabel}
											</text>

											<g
												role="button"
												tabindex="0"
												aria-label={`${pt.row.label}: ${pt.hasData ? `${pt.val} ${activeTrendMeta.unit}, ${pt.row.wins}W ${pt.row.draws}D ${pt.row.losses}L` : 'No completed matches'}`}
												aria-pressed={isFocused}
												onclick={() => (selectedTrendSeasonId = pt.row.season_id)}
												onmouseenter={() => (selectedTrendSeasonId = pt.row.season_id)}
												onfocus={() => (selectedTrendSeasonId = pt.row.season_id)}
												onkeydown={(e) => handleTrendPointKeydown(e, pt.row.season_id)}
												class="cursor-pointer trend-point"
											>
												<circle cx={pt.x} cy={pt.hasData ? pt.y : trendScale.baselineY} r="18" fill="transparent" />
												{#if pt.hasData}
													{#if isFocused}
														<circle
															cx={pt.x}
															cy={pt.y}
															r="9"
															fill="none"
															stroke="var(--color-accent-2)"
															stroke-width="2"
														/>
													{/if}
													<circle
														cx={pt.x}
														cy={pt.y}
														r={isFocused ? '6' : '4.5'}
														fill={isFocused ? 'var(--color-accent-2)' : 'var(--color-accent)'}
														stroke="var(--color-paper)"
														stroke-width="2"
													/>
												{:else}
													<circle
														cx={pt.x}
														cy={trendScale.baselineY}
														r="4"
														fill="var(--color-paper-2)"
														stroke="var(--color-muted)"
														stroke-width="1.5"
													/>
												{/if}
											</g>
										{/each}
									</svg>
								</div>
							</div>

							<!-- Touch-Friendly 44px Season Selector Strip -->
							<div class="flex items-center gap-2 overflow-x-auto pb-1">
								{#each trendsData.trends as item (item.season_id)}
									{@const isPillActive = activeTrendItem?.season_id === item.season_id}
									<button
										type="button"
										onclick={() => (selectedTrendSeasonId = item.season_id)}
										aria-pressed={isPillActive}
										class="min-h-[44px] px-3 rounded-card border text-xs font-outlier whitespace-nowrap transition-colors {isPillActive ? 'bg-paper-3 text-ink border-rule-2 font-bold' : 'bg-paper text-ink-2 border-rule hover:text-ink'}"
									>
										{shortSeasonLabel(item)}
									</button>
								{/each}
							</div>

							{#if activeTrendItem}
								<div class="border-t border-rule pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
									<div class="space-y-1">
										<div class="font-bold text-ink">{activeTrendItem.label}</div>
										<p class="text-ink-2">{activeTrendItem.arteta_milestone}</p>
									</div>
									<div class="flex items-center gap-4 num font-outlier shrink-0 flex-wrap">
										<span class="text-ink">{activeTrendItem.matches_played} P</span>
										<span class="text-success">{activeTrendItem.wins}W</span>
										<span class="text-accent-2">{activeTrendItem.draws}D</span>
										<span class="text-error">{activeTrendItem.losses}L</span>
										<span class="text-ink-2">GF {activeTrendItem.goals_for} / GA {activeTrendItem.goals_against}</span>
									</div>
								</div>
							{/if}
						</div>

						<!-- Chronological Season Milestone Breakdown Table -->
						<div class="overflow-x-auto border-t border-rule">
							<table class="w-full text-xs text-left">
								<thead class="text-muted border-b border-rule">
									<tr>
										<th class="py-3 pr-3 font-semibold">Season</th>
										<th class="py-3 px-2 font-semibold">P</th>
										<th class="py-3 px-2 font-semibold">W-D-L</th>
										<th class="py-3 px-2 font-semibold">GF / GA</th>
										<th class="py-3 px-2 font-semibold">CS</th>
										<th class="py-3 px-2 font-semibold">Win %</th>
										<th class="py-3 px-2 font-semibold">PPG</th>
										<th class="py-3 px-2 font-semibold">G/M</th>
										<th class="py-3 pl-3 font-semibold">
											{trendsData.club_id === 'arsenal' ? 'Arteta milestone' : 'Campaign context'}
										</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-rule text-ink-2">
									{#each trendsData.trends as item (item.season_id)}
										{@const isRowActive = activeTrendItem?.season_id === item.season_id}
										<tr class="transition-colors {isRowActive ? 'bg-paper-2 text-ink' : 'hover:bg-paper-2'}">
											<td class="py-1.5 pr-3 whitespace-nowrap num font-outlier">
												<button
													type="button"
													onclick={() => (selectedTrendSeasonId = item.season_id)}
													aria-pressed={isRowActive}
													class="min-h-[44px] text-left font-semibold text-ink hover:text-accent-text transition-colors"
												>
													{item.label}
												</button>
											</td>
											<td class="py-3 px-2 num font-outlier">{item.matches_played}</td>
											<td class="py-3 px-2 num font-outlier whitespace-nowrap">
												{item.wins}-{item.draws}-{item.losses}
											</td>
											<td class="py-3 px-2 num font-outlier whitespace-nowrap">
												{item.goals_for} / {item.goals_against}
											</td>
											<td class="py-3 px-2 num font-outlier">{item.clean_sheets}</td>
											<td class="py-3 px-2 num font-outlier font-semibold text-ink">
												{item.win_rate}%
											</td>
											<td class="py-3 px-2 num font-outlier">{item.points_per_game}</td>
											<td class="py-3 px-2 num font-outlier">{item.goals_per_match}</td>
											<td class="py-3 pl-3 text-muted max-w-xs">{item.arteta_milestone}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				{:else}
					<div class="py-12 border-t border-rule text-muted text-sm">
						No multi-season trend records available for this selection.
					</div>
				{/if}

			{:else if activeTab === 'h2h'}
				{#if h2hLoading}
					<div class="py-16 border-t border-rule text-muted text-sm" role="status" aria-live="polite">
						Loading head-to-head match history…
					</div>
				{:else if h2hError}
					<StateBanner
						variant="error"
						title="Opponent head-to-head unavailable"
						message={h2hError}
						onretry={runH2HQuery}
						busy={h2hLoading}
					/>
				{:else if h2hData}
					<div class="space-y-8">
						<!-- H2H Header & W-D-L Bar -->
						<div class="bg-paper-2 border-t-2 border-rule-2 p-6 space-y-5">
							<div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 border-b border-rule pb-4">
								<h2 class="text-xl font-bold text-ink wrap-heading">
									{clubList.find((c) => c.id === h2hData?.club_id)?.name || h2hData.club_id} vs {h2hData.opponent_name}
								</h2>
								<span class="text-xs text-muted">
									Venue: <strong class="text-ink-2">{h2hData.venue_filter}</strong>
								</span>
							</div>

							<div class="flex flex-wrap items-baseline justify-between gap-4">
								<div class="flex items-baseline gap-3 flex-wrap">
									<span class="text-3xl font-bold text-ink num font-outlier">
										{h2hData.matches_played === 0 ? '—' : `${h2hData.win_rate}%`}
									</span>
									<span class="text-xs text-muted">
										{h2hData.matches_played === 0
											? 'No completed meetings recorded'
											: `win rate across ${h2hData.matches_played} meetings`}
									</span>
									{#if h2hData.matches_played > 0 && h2hData.matches_played < 5}
										<span class="text-xs font-semibold text-accent-2 border border-rule px-2 py-0.5 rounded-card">
											Small sample (n = {h2hData.matches_played})
										</span>
									{/if}
								</div>
								<div class="flex items-center gap-4 text-xs num font-outlier font-semibold">
									<span class="text-success">{h2hData.wins}W</span>
									<span class="text-accent-2">{h2hData.draws}D</span>
									<span class="text-error">{h2hData.losses}L</span>
								</div>
							</div>

							{#if h2hData.matches_played > 0}
								<div class="w-full h-2.5 rounded-card bg-paper overflow-hidden flex">
									<div class="bg-success" style="width: {(h2hData.wins / h2hData.matches_played) * 100}%;" title="Wins"></div>
									<div class="bg-accent-2" style="width: {(h2hData.draws / h2hData.matches_played) * 100}%;" title="Draws"></div>
									<div class="bg-error" style="width: {(h2hData.losses / h2hData.matches_played) * 100}%;" title="Losses"></div>
								</div>
							{/if}

							<!-- GF / GA / GD / Clean Sheets Ledger -->
							<div class="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-4 border-t border-rule">
								<div>
									<span class="text-xs text-muted">Goals for</span>
									<div class="text-2xl font-bold text-ink num font-outlier mt-1">{h2hData.goals_for}</div>
								</div>
								<div>
									<span class="text-xs text-muted">Goals against</span>
									<div class="text-2xl font-bold text-ink num font-outlier mt-1">{h2hData.goals_against}</div>
								</div>
								<div>
									<span class="text-xs text-muted">Goal difference</span>
									<div class="text-2xl font-bold num font-outlier mt-1 {h2hData.goal_difference >= 0 ? 'text-success' : 'text-error'}">
										{h2hData.goal_difference > 0 ? `+${h2hData.goal_difference}` : h2hData.goal_difference}
									</div>
								</div>
								<div>
									<span class="text-xs text-muted">Clean sheets</span>
									<div class="text-2xl font-bold text-ink num font-outlier mt-1">{h2hData.clean_sheets}</div>
								</div>
							</div>
						</div>

						<!-- Recent Head-to-Head Match Rows -->
						<div class="border-t-2 border-rule-2 pt-5 space-y-4">
							<div class="flex items-baseline justify-between border-b border-rule pb-3">
								<h3 class="text-base font-bold text-ink">Head-to-head match ledger</h3>
								<span class="text-xs text-muted num font-outlier">{h2hData.recent_matches.length} fixtures</span>
							</div>

							{#if h2hData.recent_matches.length === 0}
								<p class="text-sm text-muted py-4">
									No completed head-to-head fixtures recorded for this opponent and venue filter.
								</p>
							{:else}
								<div class="divide-y divide-rule border-b border-rule">
									{#each h2hData.recent_matches as m (m.id)}
										{@const outcome = getH2HMatchOutcome(m.home_team_id, m.away_team_id, m.home_score, m.away_score, h2hData.club_id)}
										<a
											href="/matches/{encodeURIComponent(m.id)}"
											class="py-3.5 px-2 -mx-2 hover:bg-paper-2 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3"
										>
											<div class="space-y-1 min-w-0">
												<div class="flex items-center gap-2.5 text-xs text-muted">
													<span class="num font-outlier">{formatShortDate(m.utc_date)}</span>
													<span>{m.competition_name || m.competition_id || 'Competition'}</span>
													{#if m.venue}
														<span class="truncate">({m.venue})</span>
													{/if}
												</div>
												<div class="text-sm font-semibold text-ink truncate">
													{m.home_team_name} vs {m.away_team_name}
												</div>
											</div>

											<div class="flex items-center gap-3 shrink-0">
												<span class="num font-outlier font-bold text-base text-ink">
													{m.home_score ?? 0} : {m.away_score ?? 0}
												</span>
												<span
													class="num w-6 text-center text-xs font-semibold {outcome === 'W' ? 'text-success' : outcome === 'D' ? 'text-accent-2' : 'text-error'}"
												>
													{outcome}
												</span>
											</div>
										</a>
									{/each}
								</div>
							{/if}
						</div>
					</div>
				{:else}
					<div class="py-12 border-t border-rule text-muted text-sm">
						No opponent head-to-head records found for this selection.
					</div>
				{/if}

			{:else if activeTab === 'squad'}
				{#if squadLoading}
					<div class="py-16 border-t border-rule text-muted text-sm" role="status" aria-live="polite">
						Computing Arsenal squad head-to-head metrics…
					</div>
				{:else if squadError}
					<StateBanner
						variant="error"
						title="Squad comparison unavailable"
						message={squadError}
						onretry={runSquadComparison}
						busy={squadLoading}
					/>
				{:else if playerComparison}
					{@const p1 = playerComparison.player1.player}
					{@const p2 = playerComparison.player2.player}
					<div class="space-y-8">
						<!-- Players Header -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<a
								href="/squad/{encodeURIComponent(p1.id)}"
								class="bg-paper-2 border-t-2 border-accent p-5 space-y-2 hover:bg-paper-3 transition-colors block"
							>
								<div class="flex items-center justify-between text-xs text-muted">
									<span class="text-accent-text font-semibold">Player A</span>
									<span class="num font-outlier">{p1.appearances} apps ({p1.minutes_played} min)</span>
								</div>
								<div class="flex items-baseline gap-3">
									<span class="num font-display font-bold text-2xl text-accent-text">#{p1.jersey_number}</span>
									<h2 class="text-lg font-bold text-ink card-headline">{p1.name}</h2>
								</div>
								<p class="text-xs text-muted">{p1.position}, {p1.nationality}</p>
							</a>

							<a
								href="/squad/{encodeURIComponent(p2.id)}"
								class="bg-paper-2 border-t-2 border-accent-2 p-5 space-y-2 hover:bg-paper-3 transition-colors block"
							>
								<div class="flex items-center justify-between text-xs text-muted">
									<span class="text-accent-2 font-semibold">Player B</span>
									<span class="num font-outlier">{p2.appearances} apps ({p2.minutes_played} min)</span>
								</div>
								<div class="flex items-baseline gap-3">
									<span class="num font-display font-bold text-2xl text-accent-2">#{p2.jersey_number}</span>
									<h2 class="text-lg font-bold text-ink card-headline">{p2.name}</h2>
								</div>
								<p class="text-xs text-muted">{p2.position}, {p2.nationality}</p>
							</a>
						</div>

						<!-- Normalized Comparison Bars -->
						<div class="border-t-2 border-rule-2 pt-5 space-y-6">
							<div class="flex items-baseline justify-between border-b border-rule pb-3 flex-wrap gap-2">
								<h3 class="text-base font-bold text-ink">Normalized head-to-head comparison</h3>
								<div class="flex items-center gap-4 text-xs text-ink-2">
									<span class="inline-flex items-center gap-1.5">
										<span class="w-2.5 h-2.5 rounded-card bg-accent inline-block"></span>
										{p1.short_name}
									</span>
									<span class="inline-flex items-center gap-1.5">
										<span class="w-2.5 h-2.5 rounded-card bg-accent-2 inline-block"></span>
										{p2.short_name}
									</span>
								</div>
							</div>

							<div class="divide-y divide-rule">
								{#each squadComparisonBars as bar (bar.key)}
									<div class="py-4 space-y-3">
										<div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1">
											<span class="text-sm font-semibold text-ink">{bar.label}</span>
											<span class="text-xs text-muted">{bar.note}</span>
										</div>

										<div class="space-y-2 text-xs">
											<div class="grid grid-cols-12 items-center gap-3">
												<span class="col-span-4 sm:col-span-3 text-ink-2 truncate font-medium">{p1.short_name}</span>
												<div class="col-span-5 sm:col-span-6 h-2.5 bg-paper-2 rounded-card overflow-hidden">
													<div class="h-full bg-accent" style="width: {bar.p1Pct}%;"></div>
												</div>
												<span class="col-span-3 text-right num font-outlier font-semibold text-ink">{bar.p1Text}</span>
											</div>

											<div class="grid grid-cols-12 items-center gap-3">
												<span class="col-span-4 sm:col-span-3 text-ink-2 truncate font-medium">{p2.short_name}</span>
												<div class="col-span-5 sm:col-span-6 h-2.5 bg-paper-2 rounded-card overflow-hidden">
													<div class="h-full bg-accent-2" style="width: {bar.p2Pct}%;"></div>
												</div>
												<span class="col-span-3 text-right num font-outlier font-semibold text-ink">{bar.p2Text}</span>
											</div>
										</div>
									</div>
								{/each}
							</div>
						</div>

						<!-- Tactical Verdict Summary -->
						<div class="bg-paper-2 border-t-2 border-rule-2 p-5 space-y-2">
							<div class="text-xs font-semibold text-accent-2">Tactical verdict</div>
							<p class="text-sm text-ink leading-relaxed">{playerComparison.comparison_summary}</p>
						</div>
					</div>
				{:else}
					<div class="py-12 border-t border-rule text-muted text-sm">
						Select two distinct Arsenal players from the workbench controls to compare their output.
					</div>
				{/if}

			{:else}
				<HistoricalPitchExplorer
					matches={data.historicalMatches}
					initialDetail={data.initialHistoricalDetail}
					initialMatchId={data.activeHistoricalMatchId}
					initialMatchesError={data.historicalMatchesError}
					initialDetailError={data.initialHistoricalDetailError}
					showBackLink={false}
				/>
			{/if}
			</div>
		</main>
	</div>

	<!-- Create Insight Modal -->
	{#if isModalOpen}
		<div class="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4">
			<button
				type="button"
				tabindex="-1"
				aria-label="Close modal"
				onclick={() => (isModalOpen = false)}
				class="fixed inset-0 w-full h-full bg-paper/85 cursor-default"
			></button>
			<div
				role="dialog"
				aria-modal="true"
				aria-labelledby="ins-modal-title"
				use:focusTrap={{
					active: isModalOpen,
					onEscape: () => (isModalOpen = false),
					initialFocusSelector: '#ins-title'
				}}
				class="relative z-10 bg-paper-2 border-t-2 border-rule-2 max-w-lg w-full p-6 space-y-5"
			>
				<div class="flex items-center justify-between border-b border-rule pb-3">
					<h3 id="ins-modal-title" class="text-base font-bold text-ink">Publish shareable insight</h3>
					<button
						type="button"
						onclick={() => (isModalOpen = false)}
						class="min-h-[44px] px-2 text-muted hover:text-ink text-xs font-semibold"
					>
						Close
					</button>
				</div>

				<div class="space-y-4 text-xs">
					<div>
						<div class="flex items-center justify-between mb-1">
							<label for="ins-title" class="font-semibold text-ink-2">Insight title</label>
							<span class="num font-outlier text-muted">{trimmedInsightTitle.length}/200</span>
						</div>
						<input
							id="ins-title"
							type="text"
							minlength={3}
							maxlength={200}
							bind:value={insightTitle}
							class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-ink"
						/>
						{#if trimmedInsightTitle.length < 3}
							<p class="text-xs text-error mt-1">Title must be at least 3 characters.</p>
						{/if}
					</div>

					<div>
						<div class="flex items-center justify-between mb-1">
							<label for="ins-desc" class="font-semibold text-ink-2">Notes &amp; description (optional)</label>
							<span class="num font-outlier text-muted">{insightDesc.length}/500</span>
						</div>
						<textarea
							id="ins-desc"
							rows="3"
							maxlength={500}
							bind:value={insightDesc}
							class="w-full bg-paper border border-rule rounded-card p-3 text-ink"
						></textarea>
					</div>

					<div class="border-t border-rule pt-3 text-xs text-muted space-y-1">
						<p>
							<strong class="text-ink-2">Metric:</strong>
							{getMetricLabel(result?.metric || resultSnapshotMeta?.metric || metric)}
						</p>
						<p>
							<strong class="text-ink-2">Venue filter:</strong>
							{result?.venue_filter || resultSnapshotMeta?.venue || venue}
						</p>
						{#if (resultSnapshotMeta?.season_id || selectedSeason) !== 'all'}
							<p>
								<strong class="text-ink-2">Season snapshot:</strong>
								{seasons.find((s) => s.id === (resultSnapshotMeta?.season_id || selectedSeason))?.label || (resultSnapshotMeta?.season_id || selectedSeason)}
							</p>
						{/if}
						<p>
							This insight stores the verified query parameters and statistical snapshot as an immutable record.
						</p>
					</div>
				</div>

				<div class="flex items-center justify-end gap-3 pt-2 flex-wrap">
					{#if modalError}
						<div role="alert" class="mr-auto text-xs text-error flex items-center gap-2">
							<span>{modalError.message}</span>
							{#if modalError.isAuth}
								<a href="/login?next=/lab" class="underline text-ink font-semibold hover:text-accent-text">Sign in</a>
							{/if}
						</div>
					{/if}
					<button
						type="button"
						onclick={() => (isModalOpen = false)}
						class="min-h-[44px] px-3 rounded-card text-xs font-semibold text-ink-2 hover:text-ink"
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={submitInsight}
						disabled={isSavingInsight || !isInsightTitleValid}
						class="min-h-[44px] px-4 rounded-card text-xs font-semibold bg-accent hover:opacity-95 disabled:opacity-50 text-accent-ink transition-opacity"
					>
						{publishBtnLabel}
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.wrap-heading {
		overflow-wrap: break-word;
		min-width: 0;
	}
	.trend-point:focus-visible {
		outline: 2px solid var(--color-focus);
		outline-offset: 3px;
	}
</style>
