import { fetchNotifications, fetchUnreadNotificationsCount } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || 'guest_user';

	const [notifications, unreadCount] = await Promise.all([
		fetchNotifications(userId),
		fetchUnreadNotificationsCount(userId)
	]);

	return {
		notifications,
		unreadCount,
		currentUserId: userId
	};
};
