import { fetchConversationsResult, fetchClubs } from '$lib/api/football';
import { searchSupporters } from '$lib/api/community';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent, url, fetch }) => {
	const { user, session, profile } = await parent();
	const userId = user?.id || profile?.id || null;
	const accessToken = session?.access_token ?? null;
	const isSignedIn = Boolean(user && userId && accessToken);

	const [conversationsResult, clubs, initialSupporters] = await Promise.all([
		isSignedIn
			? fetchConversationsResult(userId ?? undefined, accessToken, fetch)
			: Promise.resolve({ data: [], error: null, status: 200, isFallback: false }),
		fetchClubs(),
		isSignedIn ? searchSupporters('', 12, accessToken).catch(() => []) : Promise.resolve([])
	]);

	const recipientParam = url.searchParams.get('recipient');
	const recipientName = url.searchParams.get('name') || 'Supporter';
	const recipientClub = url.searchParams.get('club') || 'arsenal';
	const initialConversationId = url.searchParams.get('c');

	return {
		conversations: conversationsResult.data,
		conversationsError: conversationsResult.error,
		clubs,
		initialSupporters,
		initialConversationId,
		currentUserId: userId,
		initialRecipient: recipientParam ? { id: recipientParam, name: recipientName, club: recipientClub } : null
	};
};
