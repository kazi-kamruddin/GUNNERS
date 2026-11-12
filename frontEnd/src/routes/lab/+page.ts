import {
	fetchInsights,
	queryAnalytics,
	fetchSeasons,
	fetchMultiSeasonTrends,
	fetchOpponentH2H,
	fetchSquad,
	comparePlayers,
	fetchHistoricalMatches,
	fetchHistoricalMatchDetail
} from '$lib/api/football';
import type { Player } from '$lib/types/football';
import type { PageLoad } from './$types';

type LabTab = 'query' | 'trends' | 'h2h' | 'squad' | 'pitch';
const VALID_TABS: ReadonlySet<string> = new Set(['query', 'trends', 'h2h', 'squad', 'pitch']);

function pickDefaultPair(squad: Player[], p1Param: string | null, p2Param: string | null): [string, string] {
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

export const load: PageLoad = async ({ url }) => {
	const tabParam = url.searchParams.get('tab') || 'query';
	const initialTab: LabTab = VALID_TABS.has(tabParam) ? (tabParam as LabTab) : 'query';

	const metric = url.searchParams.get('metric') || 'win_rate';
	const teamsParam = url.searchParams.get('teams');
	const team_ids = teamsParam ? teamsParam.split(',').filter(Boolean) : ['arsenal'];
	const venue = url.searchParams.get('venue') || 'all';
	const seasonId = url.searchParams.get('season') || undefined;
	const opponentId = url.searchParams.get('opponent') || 'chelsea';
	const p1Param = url.searchParams.get('p1');
	const p2Param = url.searchParams.get('p2');
	const matchParam = url.searchParams.get('match');

	const [
		insights,
		initialResult,
		seasons,
		initialTrends,
		initialH2H,
		squad,
		historicalMatches
	] = await Promise.all([
		fetchInsights(),
		queryAnalytics({
			metric,
			team_ids,
			venue,
			season_id: seasonId
		}),
		fetchSeasons(),
		fetchMultiSeasonTrends('arsenal', venue),
		fetchOpponentH2H(opponentId, 'arsenal', venue),
		fetchSquad('arsenal'),
		fetchHistoricalMatches()
	]);

	const [initialCompare1Id, initialCompare2Id] = pickDefaultPair(squad, p1Param, p2Param);
	const activeHistoricalMatchId =
		matchParam || (historicalMatches.length > 0 ? historicalMatches[0].id : 'hist_ars_barca_2011');

	const [initialPlayerComparison, initialHistoricalDetail] = await Promise.all([
		comparePlayers(initialCompare1Id, initialCompare2Id),
		fetchHistoricalMatchDetail(activeHistoricalMatchId)
	]);

	return {
		initialTab,
		initialMetric: metric,
		initialTeamIds: team_ids,
		initialVenue: venue,
		initialResult,
		insights,
		seasons,
		activeSeasonId: seasonId || 'all',
		initialTrends,
		initialOpponentId: initialH2H?.opponent_id || opponentId,
		initialH2H,
		squad,
		initialCompare1Id,
		initialCompare2Id,
		initialPlayerComparison,
		historicalMatches,
		activeHistoricalMatchId,
		initialHistoricalDetail
	};
};
