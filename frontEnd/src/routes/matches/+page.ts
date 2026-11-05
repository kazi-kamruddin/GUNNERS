import { fetchMatches, fetchMatchSummary, fetchSyncStatus } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const compId = url.searchParams.get('comp') || undefined;
	const status = url.searchParams.get('status') || undefined;

	const [matches, summary, syncStatus] = await Promise.all([
		fetchMatches({ club_id: 'arsenal', competition_id: compId, status }),
		fetchMatchSummary('arsenal'),
		fetchSyncStatus()
	]);

	return {
		initialMatches: matches,
		initialSummary: summary,
		syncStatus,
		initialClubId: 'arsenal'
	};
};
