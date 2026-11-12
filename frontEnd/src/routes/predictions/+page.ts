import { fetchUpcomingPredictions, fetchLeaderboard, fetchClubs, fetchSeasons } from '$lib/api/football';
import { fetchPredictionHistory } from '$lib/api/community';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;
	const isSignedIn = Boolean(userId && accessToken);

	const [upcoming, leaderboard, clubs, seasons, history] = await Promise.all([
		fetchUpcomingPredictions(userId ?? undefined, accessToken),
		fetchLeaderboard(),
		fetchClubs(),
		fetchSeasons(),
		isSignedIn ? fetchPredictionHistory(accessToken) : Promise.resolve([])
	]);

	return {
		upcoming,
		leaderboard,
		clubs,
		seasons,
		history,
		currentUserId: userId,
		userName: profile?.display_name || session?.user?.email?.split('@')[0] || 'Supporter',
		userClubId: profile?.favorite_club_id || 'arsenal'
	};
};
