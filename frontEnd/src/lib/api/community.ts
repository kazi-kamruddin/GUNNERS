import {
	API_BASE,
	buildHeaders,
	fetchWithTimeout,
	getApiAccessToken,
	throwApiError,
	toNetworkApiError,
	type ApiResult
} from '$lib/api/football';
import type { Post, PostComment, PredictionHistoryItem, SupporterSummary } from '$lib/types/football';

export async function updateTerracePost(
	postId: string,
	payload: { content: string; image_url?: string | null },
	accessToken?: string | null
): Promise<Post> {
	try {
		const res = await fetch(`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}`, {
			method: 'PATCH',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(payload)
		});
		if (!res.ok) await throwApiError(res, 'Failed to update post');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while updating post');
	}
}

export async function updateTerraceComment(
	postId: string,
	commentId: string,
	content: string,
	accessToken?: string | null
): Promise<PostComment> {
	try {
		const res = await fetch(
			`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}/comments/${encodeURIComponent(commentId)}`,
			{
				method: 'PATCH',
				headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
				body: JSON.stringify({ content })
			}
		);
		if (!res.ok) await throwApiError(res, 'Failed to update comment');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while updating comment');
	}
}

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
		const res = await fetchWithTimeout(`${API_BASE}/predictions/history`, {
			headers: buildHeaders(token)
		});
		if (!res.ok) return [];
		return await res.json();
	} catch {
		return [];
	}
}

export async function fetchPredictionHistoryResult(
	accessToken?: string | null,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<PredictionHistoryItem[]>> {
	const token = accessToken ?? getApiAccessToken();
	if (!token) {
		return { data: [], error: null, status: 401, isFallback: false };
	}
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/predictions/history`,
			{ headers: buildHeaders(token) },
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, `Failed to load prediction history (${res.status})`);
		const data = (await res.json()) as PredictionHistoryItem[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const apiErr = toNetworkApiError(err, 'Unable to load prediction history.');
		return { data: [], error: apiErr.detail, status: apiErr.status, isFallback: false };
	}
}
