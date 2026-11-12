import {
	ApiError,
	fetchInsightsResult,
	queryAnalyticsStrict,
	fetchSeasons,
	fetchMultiSeasonTrendsStrict,
	fetchOpponentH2HStrict,
	fetchSquadResult,
	comparePlayersStrict,
	fetchHistoricalMatchesResult,
	fetchHistoricalMatchDetailStrict
} from '$lib/api/football';
import type { Player } from '$lib/types/football';
import type { PageLoad } from './$types';

type LabTab = 'query' | 'trends' | 'h2h' | 'squad' | 'pitch';
type TrendMetricKey = 'win_rate' | 'points_per_game' | 'goals_per_match' | 'clean_sheet_rate';

const VALID_TABS: ReadonlySet<string> = new Set(['query', 'trends', 'h2h', 'squad', 'pitch']);
const VALID_TREND_METRICS: ReadonlySet<string> = new Set([
	'win_rate',
	'points_per_game',
	'goals_per_match',
	'clean_sheet_rate'
]);

function pickDefaultPair(
	squad: Player[],
	p1Param: string | null,
	p2Param: string | null
): [string, string] {
	if (p1Param && p2Param && p1Param !== p2Param) {
		return [p1Param, p2Param];
	}
	if (squad.length >= 2) {
		const hasSaka = squad.some((p) => p.id === 'ply_saka');
		const hasGyokeres = squad.some((p) => p.id === 'ply_gyokeres');
		if (hasSaka && hasGyokeres) {
			return ['ply_saka', 'ply_gyokeres'];
		}
		const attackingPool = squad.filter(
			(p) => p.position === 'Attacker' || p.position === 'Midfielder'
		);
		const pool = attackingPool.length >= 2 ? attackingPool : squad;
		return [pool[0].id, pool[1].id];
	}
	return [p1Param || 'ply_saka', p2Param || 'ply_gyokeres'];
}

function getErrMessage(reason: unknown, fallback: string): string {
	if (reason instanceof ApiError) return reason.detail;
	if (reason instanceof Error && reason.message) return reason.message;
	return fallback;
}

export const load: PageLoad = async ({ url, fetch }) => {
	const tabParam = url.searchParams.get('tab') || 'query';
	const initialTab: LabTab = VALID_TABS.has(tabParam) ? (tabParam as LabTab) : 'query';

	const metric = url.searchParams.get('metric') || 'win_rate';
	const teamsParam = url.searchParams.get('teams');
	const team_ids = teamsParam ? teamsParam.split(',').filter(Boolean) : ['arsenal'];
	const venue = url.searchParams.get('venue') || 'all';
	const seasonId = url.searchParams.get('season') || undefined;

	const trendsClub = url.searchParams.get('club') || 'arsenal';
	const tMetricParam = url.searchParams.get('tmetric') || 'win_rate';
	const initialTrendMetric: TrendMetricKey = VALID_TREND_METRICS.has(tMetricParam)
		? (tMetricParam as TrendMetricKey)
		: 'win_rate';

	const h2hClub = url.searchParams.get('hclub') || 'arsenal';
	const opponentId = url.searchParams.get('opponent') || 'chelsea';
	const p1Param = url.searchParams.get('p1');
	const p2Param = url.searchParams.get('p2');
	const matchParam = url.searchParams.get('match');

	const [
		insightsRes,
		querySettled,
		seasons,
		trendsSettled,
		h2hSettled,
		squadRes,
		historicalRes
	] = await Promise.all([
		fetchInsightsResult(undefined, fetch),
		queryAnalyticsStrict(
			{
				metric,
				team_ids,
				venue,
				season_id: seasonId
			},
			fetch
		)
			.then((data) => ({ data, error: null as string | null }))
			.catch((err) => ({ data: null, error: getErrMessage(err, 'Unable to compute Data Lab analytics.') })),
		fetchSeasons(),
		fetchMultiSeasonTrendsStrict(trendsClub, venue, fetch)
			.then((data) => ({ data, error: null as string | null }))
			.catch((err) => ({ data: null, error: getErrMessage(err, 'Unable to load multi-season trends.') })),
		fetchOpponentH2HStrict(opponentId, h2hClub, venue, fetch)
			.then((data) => ({ data, error: null as string | null }))
			.catch((err) => ({ data: null, error: getErrMessage(err, 'Unable to load opponent head-to-head ledger.') })),
		fetchSquadResult('arsenal', undefined, fetch),
		fetchHistoricalMatchesResult(fetch)
	]);

	const squad = squadRes.data;
	const historicalMatches = historicalRes.data;
	const [initialCompare1Id, initialCompare2Id] = pickDefaultPair(squad, p1Param, p2Param);
	const activeHistoricalMatchId =
		matchParam || (historicalMatches.length > 0 ? historicalMatches[0].id : 'hist_ars_barca_2011');

	const [squadCompareSettled, histDetailSettled] = await Promise.all([
		comparePlayersStrict(initialCompare1Id, initialCompare2Id, fetch)
			.then((data) => ({ data, error: null as string | null }))
			.catch((err) => ({ data: null, error: getErrMessage(err, 'Unable to compare the selected players.') })),
		fetchHistoricalMatchDetailStrict(activeHistoricalMatchId, fetch)
			.then((data) => ({ data, error: data ? null : 'Historical match telemetry was not found.' }))
			.catch((err) => ({ data: null, error: getErrMessage(err, 'Unable to load historical match telemetry.') }))
	]);

	return {
		initialTab,
		initialMetric: metric,
		initialTeamIds: team_ids,
		initialVenue: venue,
		initialResult: querySettled.data,
		initialQueryError: querySettled.error,
		insights: insightsRes.data,
		insightsError: insightsRes.error,
		seasons,
		activeSeasonId: seasonId || 'all',
		initialTrendsClub: trendsClub,
		initialTrendMetric,
		initialTrends: trendsSettled.data,
		initialTrendsError: trendsSettled.error,
		initialH2HClub: h2hClub,
		initialOpponentId: h2hSettled.data?.opponent_id || opponentId,
		initialH2H: h2hSettled.data,
		initialH2HError: h2hSettled.error,
		squad,
		squadListError: squadRes.error,
		initialCompare1Id,
		initialCompare2Id,
		initialPlayerComparison: squadCompareSettled.data,
		initialSquadError: squadCompareSettled.error,
		historicalMatches,
		historicalMatchesError: historicalRes.error,
		activeHistoricalMatchId,
		initialHistoricalDetail: histDetailSettled.data,
		initialHistoricalDetailError: histDetailSettled.error
	};
};
