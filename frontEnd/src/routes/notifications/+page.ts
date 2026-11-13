import { fetchNotificationsResult, fetchUnreadNotificationsCount } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent, fetch }) => {
	const { user, session, profile } = await parent();
	const userId = user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;

	if (!user || !userId || !accessToken) {
		return {
			notifications: [],
			unreadCount: 0,
			currentUserId: null,
			notificationsError: null as string | null
		};
	}

	const [notificationsResult, unreadCount] = await Promise.all([
		fetchNotificationsResult(userId, accessToken, fetch),
		fetchUnreadNotificationsCount(userId, accessToken)
	]);

	return {
		notifications: notificationsResult.data,
		unreadCount,
		currentUserId: userId,
		notificationsError: notificationsResult.error
	};
};
