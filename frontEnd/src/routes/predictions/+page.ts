import { fetchUpcomingPredictions, fetchLeaderboard, fetchClubs } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;

	const [upcoming, leaderboard, clubs] = await Promise.all([
		fetchUpcomingPredictions(userId ?? undefined, accessToken),
		fetchLeaderboard(),
		fetchClubs()
	]);

	return {
		upcoming,
		leaderboard,
		clubs,
		currentUserId: userId,
		userName: profile?.display_name || session?.user?.email?.split('@')[0] || 'Supporter',
		userClubId: profile?.favorite_club_id || 'arsenal'
	};
};
