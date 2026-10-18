import { fetchMatches, fetchMatchSummary, fetchSyncStatus } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const clubId = url.searchParams.get('club') || 'arsenal';
	const compId = url.searchParams.get('comp') || undefined;
	const status = url.searchParams.get('status') || undefined;

	const [matches, summary, syncStatus] = await Promise.all([
		fetchMatches({ club_id: clubId, competition_id: compId, status }),
		fetchMatchSummary(clubId),
		fetchSyncStatus()
	]);

	return {
		initialMatches: matches,
		initialSummary: summary,
		syncStatus,
		initialClubId: clubId
	};
};
