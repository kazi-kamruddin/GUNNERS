import { fetchConversations, fetchClubs } from '$lib/api/football';
import { searchSupporters } from '$lib/api/community';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent, url }) => {
	const { session, profile } = await parent();
	const userId = session?.user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;
	const isSignedIn = Boolean(userId && accessToken);

	const [conversations, clubs, initialSupporters] = await Promise.all([
		isSignedIn ? fetchConversations(userId ?? undefined, accessToken) : Promise.resolve([]),
		fetchClubs(),
		isSignedIn ? searchSupporters('', 12, accessToken).catch(() => []) : Promise.resolve([])
	]);

	const recipientParam = url.searchParams.get('recipient');
	const recipientName = url.searchParams.get('name') || 'Supporter';
	const recipientClub = url.searchParams.get('club') || 'arsenal';
	const initialConversationId = url.searchParams.get('c');

	return {
		conversations,
		clubs,
		initialSupporters,
		initialConversationId,
		currentUserId: userId,
		initialRecipient: recipientParam ? { id: recipientParam, name: recipientName, club: recipientClub } : null
	};
};
