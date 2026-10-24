import { fetchUpcomingPredictions, fetchLeaderboard, fetchClubs } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || 'guest_user';

	const [upcoming, leaderboard, clubs] = await Promise.all([
		fetchUpcomingPredictions(userId),
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
