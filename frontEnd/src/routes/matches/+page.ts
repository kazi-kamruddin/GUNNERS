import {
	fetchMatchesResult,
	fetchMatchSummaryResult,
	fetchSyncStatus,
	fetchSeasons
} from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
	const compParam = url.searchParams.get('comp') || url.searchParams.get('competition') || 'ALL';
	const statusParam = url.searchParams.get('status') || 'ALL';
	const seasonId = url.searchParams.get('season') || 'all';

	const [matchesRes, summaryRes, syncStatus, seasons] = await Promise.all([
		fetchMatchesResult(
			{
				club_id: 'arsenal',
				competition_id: compParam !== 'ALL' ? compParam : undefined,
				status: statusParam !== 'ALL' ? statusParam : undefined,
				season_id: seasonId === 'all' ? undefined : seasonId
			},
			fetch
		),
		fetchMatchSummaryResult('arsenal', fetch),
		fetchSyncStatus(),
		fetchSeasons()
	]);

	return {
		initialMatches: matchesRes.data,
		matchesError: matchesRes.error,
		initialSummary: summaryRes.data,
		summaryError: summaryRes.error,
		syncStatus,
		seasons,
		activeSeasonId: seasonId,
		activeComp: compParam,
		activeStatus: statusParam,
		initialClubId: 'arsenal'
	};
};
