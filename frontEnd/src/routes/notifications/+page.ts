import { fetchNotifications, fetchUnreadNotificationsCount } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;

	if (!userId || !accessToken) {
		return {
			notifications: [],
			unreadCount: 0,
			currentUserId: null
		};
	}

	const [notifications, unreadCount] = await Promise.all([
		fetchNotifications(userId, accessToken),
		fetchUnreadNotificationsCount(userId, accessToken)
	]);

	return {
		notifications,
		unreadCount,
		currentUserId: userId
	};
};
