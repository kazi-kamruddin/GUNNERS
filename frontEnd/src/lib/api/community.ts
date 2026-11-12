import {
	API_BASE,
	buildHeaders,
	getApiAccessToken,
	throwApiError,
	toNetworkApiError
} from '$lib/api/football';
import type { PredictionHistoryItem, SupporterSummary } from '$lib/types/football';

export async function deleteTerracePost(
	postId: string,
	accessToken?: string | null
): Promise<{ status: string; id: string }> {
	try {
		const res = await fetch(`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}`, {
			method: 'DELETE',
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to delete post');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while deleting post');
	}
}

export async function deleteTerraceComment(
	postId: string,
	commentId: string,
	accessToken?: string | null
): Promise<{ status: string; id: string }> {
	try {
		const res = await fetch(
			`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}/comments/${encodeURIComponent(commentId)}`,
			{
				method: 'DELETE',
				headers: buildHeaders(accessToken)
			}
		);
		if (!res.ok) await throwApiError(res, 'Failed to delete comment');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while deleting comment');
	}
}

export async function searchSupporters(
	q: string = '',
	limit: number = 20,
	accessToken?: string | null
): Promise<SupporterSummary[]> {
	try {
		const query = new URLSearchParams();
		if (q.trim()) query.set('q', q.trim());
		query.set('limit', String(limit));
		const res = await fetch(`${API_BASE}/supporters?${query.toString()}`, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to search supporters');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to search supporters');
	}
}

export async function markConversationRead(
	conversationId: string,
	accessToken?: string | null
): Promise<{ status: string; unread_count: number }> {
	try {
		const res = await fetch(
			`${API_BASE}/messages/conversations/${encodeURIComponent(conversationId)}/read`,
			{
				method: 'POST',
				headers: buildHeaders(accessToken)
			}
		);
		if (!res.ok) await throwApiError(res, 'Failed to mark conversation as read');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while marking conversation read');
	}
}

export async function fetchPredictionHistory(
	accessToken?: string | null
): Promise<PredictionHistoryItem[]> {
	const token = accessToken ?? getApiAccessToken();
	if (!token) return [];
	try {
		const res = await fetch(`${API_BASE}/predictions/history`, {
			headers: buildHeaders(token)
		});
		if (!res.ok) return [];
		return await res.json();
	} catch {
		return [];
	}
}
