import { fetchMatches, fetchMatchSummary, fetchSyncStatus, fetchSeasons } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const compId = url.searchParams.get('comp') || undefined;
	const status = url.searchParams.get('status') || undefined;
	const seasonId = url.searchParams.get('season') || 'all';

	const [matches, summary, syncStatus, seasons] = await Promise.all([
		fetchMatches({
			club_id: 'arsenal',
			competition_id: compId,
			status,
			season_id: seasonId === 'all' ? undefined : seasonId
		}),
		fetchMatchSummary('arsenal'),
		fetchSyncStatus(),
		fetchSeasons()
	]);

	return {
		initialMatches: matches,
		initialSummary: summary,
		syncStatus,
		seasons,
		activeSeasonId: seasonId,
		initialClubId: 'arsenal'
	};
};
