import {
	fetchUpcomingPredictionsStrict,
	fetchLeaderboardStrict,
	fetchClubs,
	fetchSeasons,
	getApiErrorMessage
} from '$lib/api/football';
import { fetchPredictionHistoryResult } from '$lib/api/community';
import type { LeaderboardEntry, UpcomingMatchPrediction } from '$lib/types/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent, fetch }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;
	const isSignedIn = Boolean(userId && accessToken);

	const [upcomingSettled, leaderboardSettled, clubs, seasons, historyRes] = await Promise.all([
		fetchUpcomingPredictionsStrict(userId ?? undefined, accessToken, fetch)
			.then((data) => ({ data, error: null as string | null }))
			.catch((err) => ({
				data: [] as UpcomingMatchPrediction[],
				error: getApiErrorMessage(err, 'Unable to load upcoming matchday fixtures.').detail
			})),
		fetchLeaderboardStrict(undefined, undefined, undefined, fetch)
			.then((data) => ({ data, error: null as string | null }))
			.catch((err) => ({
				data: [] as LeaderboardEntry[],
				error: getApiErrorMessage(err, 'Unable to load supporter leaderboard.').detail
			})),
		fetchClubs(),
		fetchSeasons(),
		isSignedIn
			? fetchPredictionHistoryResult(accessToken, fetch)
			: Promise.resolve({ data: [], error: null, status: 200, isFallback: false })
	]);

	return {
		upcoming: upcomingSettled.data,
		upcomingError: upcomingSettled.error,
		leaderboard: leaderboardSettled.data,
		leaderboardError: leaderboardSettled.error,
		clubs,
		seasons,
		history: historyRes.data,
		historyError: historyRes.error,
		currentUserId: userId,
		userName: profile?.display_name || session?.user?.email?.split('@')[0] || 'Supporter',
		userClubId: profile?.favorite_club_id || 'arsenal'
	};
};
