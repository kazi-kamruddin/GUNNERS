import { fetchConversations, fetchClubs } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent, url }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;

	const [conversations, clubs] = await Promise.all([
		userId && accessToken ? fetchConversations(userId, accessToken) : Promise.resolve([]),
		fetchClubs()
	]);

	const recipientParam = url.searchParams.get('recipient');
	const recipientName = url.searchParams.get('name') || 'Supporter';
	const recipientClub = url.searchParams.get('club') || 'arsenal';

	return {
		conversations,
		clubs,
		currentUserId: userId,
		initialRecipient: recipientParam ? { id: recipientParam, name: recipientName, club: recipientClub } : null
	};
};
