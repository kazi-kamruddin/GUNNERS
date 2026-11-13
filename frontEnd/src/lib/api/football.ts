import type {
	Club,
	Season,
	Match,
	MatchSummary,
	SyncStatus,
	AnalyticsResponse,
	MultiSeasonTrendsResponse,
	OpponentH2HResponse,
	Insight,
	InsightCreatePayload,
	Post,
	PostComment,
	PostCreatePayload,
	DirectMessage,
	Conversation,
	Player,
	PlayerComparison,
	Prediction,
	UpcomingMatchPrediction,
	LeaderboardEntry,
	Notification,
	SupporterProfile,
	HistoricalMatchSummary,
	HistoricalMatchDetail,
	TopicTag,
	FormationPreset,
	TacticalBoard,
	TacticalBoardCreatePayload,
	NewsFeed,
	NewsItem
} from '$lib/types/football';

export const API_BASE = (import.meta.env.PUBLIC_API_URL as string) || 'http://localhost:8000/api/v1';

export interface ApiResult<T> {
	data: T;
	error: string | null;
	status: number;
	isFallback: boolean;
}

export class ApiError extends Error {
	status: number;
	detail: string;
	isNetworkError: boolean;

	constructor(status: number, detail: string, isNetworkError = status === 0) {
		super(detail);
		this.name = 'ApiError';
		this.status = status;
		this.detail = detail;
		this.isNetworkError = isNetworkError;
	}
}

export async function fetchWithTimeout(
	input: RequestInfo | URL,
	init: RequestInit = {},
	timeoutMs = 15000,
	fetchFn: typeof fetch = fetch
): Promise<Response> {
	const controller = new AbortController();
	let timedOut = false;

	const externalSignal = init.signal;
	const onExternalAbort = () => controller.abort(externalSignal?.reason);
	if (externalSignal) {
		if (externalSignal.aborted) {
			controller.abort(externalSignal.reason);
		} else {
			externalSignal.addEventListener('abort', onExternalAbort, { once: true });
		}
	}

	const timer = setTimeout(() => {
		timedOut = true;
		controller.abort(new DOMException('Request timed out', 'TimeoutError'));
	}, timeoutMs);

	try {
		return await fetchFn(input, { ...init, signal: controller.signal });
	} catch (err) {
		if (timedOut) {
			throw new ApiError(
				0,
				'Request timed out — the Arsenal data service may be waking from cold start.',
				true
			);
		}
		throw err;
	} finally {
		clearTimeout(timer);
		externalSignal?.removeEventListener('abort', onExternalAbort);
	}
}

let currentAccessToken: string | null = null;

export function setApiAccessToken(token: string | null): void {
	currentAccessToken = token;
}

export function getApiAccessToken(): string | null {
	return currentAccessToken;
}

export function buildHeaders(
	accessToken?: string | null,
	extra?: Record<string, string>
): Record<string, string> {
	const headers: Record<string, string> = { ...(extra || {}) };
	const token = accessToken ?? currentAccessToken;
	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}
	return headers;
}

export async function throwApiError(res: Response, fallbackMessage: string): Promise<never> {
	let detail = fallbackMessage;
	try {
		const data = await res.json();
		if (typeof data?.detail === 'string' && data.detail.trim()) {
			detail = data.detail;
		} else if (Array.isArray(data?.detail) && data.detail.length > 0) {
			const messages = data.detail
				.map((item: { msg?: string }) => (typeof item?.msg === 'string' ? item.msg : ''))
				.filter(Boolean);
			if (messages.length > 0) detail = messages.join('; ');
		} else if (typeof data?.message === 'string' && data.message.trim()) {
			detail = data.message;
		}
	} catch {
		// Ignore non-JSON error bodies
	}
	throw new ApiError(res.status, detail);
}

export function toNetworkApiError(err: unknown, fallbackMessage: string): ApiError {
	if (err instanceof ApiError) return err;
	if (err instanceof DOMException && err.name === 'TimeoutError') {
		return new ApiError(
			0,
			'Request timed out — the Arsenal data service may be waking from cold start.',
			true
		);
	}
	return new ApiError(0, err instanceof Error && err.message ? err.message : fallbackMessage, true);
}

export async function fetchSeasons(): Promise<Season[]> {
	try {
		const res = await fetch(`${API_BASE}/matches/seasons`);
		if (!res.ok) throw new Error('Failed to fetch seasons');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching seasons, returning fallback Arteta timeline');
		return [
			{
				id: '2026-2027-PL',
				competition_id: 'PL',
				start_year: 2026,
				end_year: 2027,
				is_current: true,
				label: '2026/27 (Current Campaign)',
				headline: 'Active Running Season & Live Matchdays',
				arteta_milestone: 'Live campaign tracking: Premier League title quest and European knockout stages.'
			},
			{
				id: '2025-2026-PL',
				competition_id: 'PL',
				start_year: 2025,
				end_year: 2026,
				is_current: false,
				label: '2025/26',
				headline: 'Elite Continental & Domestic Chase',
				arteta_milestone: 'Title contention, deep Champions League knockout run, and peak squad maturity.'
			},
			{
				id: '2024-2025-PL',
				competition_id: 'PL',
				start_year: 2024,
				end_year: 2025,
				is_current: false,
				label: '2024/25',
				headline: 'Emirates Fortress & Defensive Supremacy',
				arteta_milestone: 'Gabriel-Saliba partnership concede lowest xG in Premier League.'
			},
			{
				id: '2023-2024-PL',
				competition_id: 'PL',
				start_year: 2023,
				end_year: 2024,
				is_current: false,
				label: '2023/24',
				headline: 'Record 28 Premier League Wins (89 Pts)',
				arteta_milestone: 'Club record 28 Premier League victories, 89 points, and +62 goal difference.'
			},
			{
				id: '2022-2023-PL',
				competition_id: 'PL',
				start_year: 2022,
				end_year: 2023,
				is_current: false,
				label: '2022/23',
				headline: 'Title Contenders & UCL Return (84 Pts)',
				arteta_milestone: 'Arsenal returned to the Champions League with 84 points.'
			},
			{
				id: '2021-2022-PL',
				competition_id: 'PL',
				start_year: 2021,
				end_year: 2022,
				is_current: false,
				label: '2021/22',
				headline: 'Young Guns Cultural Reset',
				arteta_milestone: 'Youngest average starting XI in England; breakout for Saka, Ødegaard, and Martinelli.'
			},
			{
				id: '2020-2021-PL',
				competition_id: 'PL',
				start_year: 2020,
				end_year: 2021,
				is_current: false,
				label: '2020/21',
				headline: 'Community Shield & Positional Rebuild',
				arteta_milestone: 'Community Shield Winners vs Liverpool; instituted Arteta 3-2-5 in-possession shape.'
			},
			{
				id: '2019-2020-PL',
				competition_id: 'PL',
				start_year: 2019,
				end_year: 2020,
				is_current: false,
				label: '2019/20',
				headline: 'Arteta Appointed & FA Cup Victory',
				arteta_milestone: 'Arteta appointed Dec 20, 2019; won the FA Cup defeating Man City & Chelsea.'
			}
		];
	}
}

export async function fetchClubs(): Promise<Club[]> {
	try {
		const res = await fetch(`${API_BASE}/clubs`);
		if (!res.ok) throw new Error('Failed to fetch clubs');
		return await res.json();
	} catch (err) {
		console.warn('API unavailable, falling back to Arsenal club metadata');
		return [
			{
				id: 'arsenal',
				slug: 'arsenal',
				name: 'Arsenal FC',
				short_name: 'Arsenal',
				league: 'Premier League',
				country: 'England',
				primary_color: '#EF0107',
				secondary_color: '#FFFFFF',
				accent_color: '#9C824A',
				crest_url: 'https://crests.football-data.org/57.png',
				is_foundation: true,
				is_active: true
			}
		];
	}
}

export async function fetchMatches(params?: {
	club_id?: string;
	competition_id?: string;
	season_id?: string;
	status?: string;
	order?: string;
	limit?: number;
}): Promise<Match[]> {
	try {
		const query = new URLSearchParams();
		if (params?.club_id) query.set('club_id', params.club_id);
		if (params?.competition_id) query.set('competition_id', params.competition_id);
		if (params?.season_id) query.set('season_id', params.season_id);
		if (params?.status) query.set('status', params.status);
		if (params?.order) query.set('order', params.order);
		if (params?.limit) query.set('limit', params.limit.toString());

		const url = `${API_BASE}/matches?${query.toString()}`;
		const res = await fetch(url);
		if (!res.ok) throw new Error(`Failed to fetch matches: ${res.status}`);
		return await res.json();
	} catch (err) {
		console.warn('API error fetching matches, falling back to local dataset');
		return getLocalFallbackMatches(params?.club_id);
	}
}

export async function fetchMatchDetail(matchId: string): Promise<Match | null> {
	try {
		const res = await fetch(`${API_BASE}/matches/${encodeURIComponent(matchId)}`);
		if (res.status === 404) return null;
		if (!res.ok) throw new Error(`Failed to fetch match detail: ${res.status}`);
		return await res.json();
	} catch (err) {
		console.warn('API error fetching match detail, checking local fallback');
		return getLocalFallbackMatches().find((m) => m.id === matchId) ?? null;
	}
}

export async function fetchMatchSummary(clubId: string): Promise<MatchSummary | null> {
	try {
		const res = await fetch(`${API_BASE}/matches/summary?club_id=${clubId}`);
		if (!res.ok) throw new Error('Failed to fetch match summary');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching match summary, calculating from fallback');
		const matches = getLocalFallbackMatches(clubId);
		const finished = matches.filter((m) => m.status === 'FINISHED');
		const scheduled = matches.filter((m) => m.status === 'SCHEDULED');
		
		const form: string[] = [];
		for (const m of finished.slice(0, 5)) {
			if (m.winner === 'DRAW') form.push('D');
			else if (
				(m.winner === 'HOME_TEAM' && m.home_team_id === clubId) ||
				(m.winner === 'AWAY_TEAM' && m.away_team_id === clubId)
			)
				form.push('W');
			else form.push('L');
		}
		form.reverse();

		return {
			club_id: clubId,
			club_name: clubId.replace('-', ' ').toUpperCase(),
			next_fixture: scheduled[0] || null,
			last_result: finished[0] || null,
			recent_form: form,
			total_completed: finished.length,
			total_scheduled: scheduled.length
		};
	}
}

export async function fetchSyncStatus(): Promise<SyncStatus | null> {
	try {
		const res = await fetch(`${API_BASE}/matches/sync-status`);
		if (!res.ok) throw new Error('Failed to fetch sync status');
		return await res.json();
	} catch (err) {
		return null;
	}
}

export async function queryAnalytics(params: {
	metric: string;
	team_ids: string[];
	venue?: string;
	season_id?: string;
}): Promise<AnalyticsResponse | null> {
	try {
		const res = await fetch(`${API_BASE}/matches/query`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				metric: params.metric,
				team_ids: params.team_ids,
				venue: params.venue || 'all',
				season_id: params.season_id
			})
		});
		if (!res.ok) throw new Error('Analytics query failed');
		return await res.json();
	} catch (err) {
		console.error('Error querying analytics:', err);
		return null;
	}
}

export async function fetchMultiSeasonTrends(
	clubId: string = 'arsenal',
	venue: string = 'all'
): Promise<MultiSeasonTrendsResponse | null> {
	try {
		const query = new URLSearchParams();
		if (clubId) query.set('club_id', clubId);
		if (venue) query.set('venue', venue);
		const res = await fetch(`${API_BASE}/matches/trends?${query.toString()}`);
		if (!res.ok) throw new Error(`Failed to fetch multi-season trends: ${res.status}`);
		return await res.json();
	} catch (err) {
		console.warn('Error fetching multi-season trends:', err);
		return null;
	}
}

export async function fetchOpponentH2H(
	opponentId: string,
	clubId: string = 'arsenal',
	venue: string = 'all'
): Promise<OpponentH2HResponse | null> {
	try {
		const query = new URLSearchParams();
		query.set('opponent_id', opponentId);
		if (clubId) query.set('club_id', clubId);
		if (venue) query.set('venue', venue);
		const res = await fetch(`${API_BASE}/matches/h2h?${query.toString()}`);
		if (!res.ok) throw new Error(`Failed to fetch opponent H2H: ${res.status}`);
		return await res.json();
	} catch (err) {
		console.warn('Error fetching opponent H2H:', err);
		return null;
	}
}

export async function createInsight(
	payload: InsightCreatePayload,
	accessToken?: string | null
): Promise<Insight> {
	try {
		const res = await fetch(`${API_BASE}/insights`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(payload)
		});
		if (!res.ok) await throwApiError(res, 'Failed to publish insight');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while publishing insight');
	}
}

export async function fetchInsights(clubId?: string): Promise<Insight[]> {
	try {
		const url = clubId ? `${API_BASE}/insights?club_id=${encodeURIComponent(clubId)}` : `${API_BASE}/insights`;
		const res = await fetch(url);
		if (!res.ok) throw new Error('Failed to fetch insights');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching insights, returning empty list');
		return [];
	}
}

export async function fetchPosts(
	clubId?: string,
	currentUserId?: string,
	search?: string,
	tag?: string,
	accessToken?: string | null
): Promise<Post[]> {
	try {
		const query = new URLSearchParams();
		if (clubId && clubId !== 'global') query.set('club_id', clubId);
		if (currentUserId) query.set('current_user_id', currentUserId);
		if (search) query.set('search', search);
		if (tag) query.set('tag', tag);

		const url = `${API_BASE}/terrace/posts?${query.toString()}`;
		const res = await fetch(url, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) throw new Error(`Failed to fetch posts: ${res.status}`);
		return await res.json();
	} catch (err) {
		console.warn('API error fetching posts, returning empty list');
		return [];
	}
}

export async function createPost(
	payload: PostCreatePayload,
	accessToken?: string | null
): Promise<Post> {
	try {
		const res = await fetch(`${API_BASE}/terrace/posts`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(payload)
		});
		if (!res.ok) await throwApiError(res, 'Failed to publish post');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while publishing post');
	}
}

export async function toggleReaction(
	postId: string,
	userId?: string | null,
	reactionType: string = 'cheer',
	accessToken?: string | null
): Promise<{ action: string; total_reactions: number }> {
	try {
		const body: Record<string, string> = { reaction_type: reactionType };
		if (userId) body.user_id = userId;
		const res = await fetch(`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}/react`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(body)
		});
		if (!res.ok) await throwApiError(res, 'Failed to update reaction');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while updating reaction');
	}
}

export async function fetchComments(postId: string): Promise<PostComment[]> {
	try {
		const res = await fetch(`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}/comments`);
		if (!res.ok) throw new Error('Failed to fetch comments');
		return await res.json();
	} catch (err) {
		return [];
	}
}

export async function createComment(
	postId: string,
	content: string,
	authorName: string = 'Supporter',
	authorClubId: string = 'arsenal',
	accessToken?: string | null
): Promise<PostComment> {
	try {
		const res = await fetch(`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}/comments`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify({ content, author_name: authorName, author_club_id: authorClubId })
		});
		if (!res.ok) await throwApiError(res, 'Failed to post reply');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while posting reply');
	}
}

export async function fetchConversations(
	userId?: string,
	accessToken?: string | null
): Promise<Conversation[]> {
	try {
		const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
		const res = await fetch(`${API_BASE}/messages/conversations${query}`, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to fetch conversations');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching conversations, returning empty list');
		return [];
	}
}

export async function createConversation(
	payload: {
		initiator_id?: string;
		recipient_id: string;
		initiator_name?: string;
		initiator_club_id?: string;
		initial_message?: string;
	},
	accessToken?: string | null
): Promise<Conversation> {
	try {
		const res = await fetch(`${API_BASE}/messages/conversations`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(payload)
		});
		if (!res.ok) await throwApiError(res, 'Failed to start conversation');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while starting conversation');
	}
}

export async function fetchMessages(
	conversationId: string,
	accessToken?: string | null
): Promise<DirectMessage[]> {
	try {
		const res = await fetch(
			`${API_BASE}/messages/conversations/${encodeURIComponent(conversationId)}/messages`,
			{
				headers: buildHeaders(accessToken)
			}
		);
		if (!res.ok) await throwApiError(res, 'Failed to load messages');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to load conversation messages');
	}
}

export async function sendMessage(
	conversationId: string,
	payload: {
		sender_id?: string;
		sender_name?: string;
		sender_club_id?: string;
		content: string;
	},
	accessToken?: string | null
): Promise<DirectMessage> {
	try {
		const res = await fetch(
			`${API_BASE}/messages/conversations/${encodeURIComponent(conversationId)}/messages`,
			{
				method: 'POST',
				headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
				body: JSON.stringify(payload)
			}
		);
		if (!res.ok) await throwApiError(res, 'Failed to send message');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while sending message');
	}
}

export async function fetchSquad(clubId?: string, position?: string): Promise<Player[]> {
	try {
		const query = new URLSearchParams();
		if (clubId) query.set('club_id', clubId);
		if (position) query.set('position', position);
		const res = await fetch(`${API_BASE}/squad?${query.toString()}`);
		if (!res.ok) throw new Error('Failed to fetch squad');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching squad, returning local fallback');
		return [];
	}
}

export async function fetchPlayer(playerId: string): Promise<Player | null> {
	try {
		const res = await fetch(`${API_BASE}/squad/${playerId}`);
		if (!res.ok) throw new Error('Failed to fetch player');
		return await res.json();
	} catch (err) {
		return null;
	}
}

export async function comparePlayers(player1Id: string, player2Id: string): Promise<PlayerComparison | null> {
	try {
		const res = await fetch(`${API_BASE}/squad/compare?player1_id=${player1Id}&player2_id=${player2Id}`);
		if (!res.ok) throw new Error('Failed to compare players');
		return await res.json();
	} catch (err) {
		return null;
	}
}

export async function fetchUpcomingPredictions(
	userId?: string,
	accessToken?: string | null
): Promise<UpcomingMatchPrediction[]> {
	try {
		const url = userId
			? `${API_BASE}/predictions/upcoming?user_id=${encodeURIComponent(userId)}`
			: `${API_BASE}/predictions/upcoming`;
		const res = await fetch(url, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) throw new Error('Failed to fetch predictions');
		return await res.json();
	} catch (err) {
		return [];
	}
}

export async function submitPrediction(
	payload: {
		user_id?: string;
		user_name?: string;
		user_club_id?: string;
		match_id: string;
		predicted_home_score: number;
		predicted_away_score: number;
	},
	accessToken?: string | null
): Promise<Prediction> {
	try {
		const res = await fetch(`${API_BASE}/predictions`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(payload)
		});
		if (!res.ok) await throwApiError(res, 'Failed to submit prediction');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while submitting prediction');
	}
}

export async function fetchLeaderboard(clubId?: string, seasonId?: string): Promise<LeaderboardEntry[]> {
	try {
		const query = new URLSearchParams();
		if (clubId) query.set('club_id', clubId);
		if (seasonId && seasonId !== 'all') query.set('season_id', seasonId);
		const qs = query.toString();
		const url = qs ? `${API_BASE}/predictions/leaderboard?${qs}` : `${API_BASE}/predictions/leaderboard`;
		const res = await fetch(url);
		if (!res.ok) throw new Error('Failed to fetch leaderboard');
		return await res.json();
	} catch (err) {
		return [];
	}
}

export async function fetchNotifications(
	userId?: string,
	accessToken?: string | null
): Promise<Notification[]> {
	try {
		const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
		const res = await fetch(`${API_BASE}/notifications${query}`, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) throw new Error('Failed to fetch notifications');
		return await res.json();
	} catch (err) {
		return [];
	}
}

export async function fetchUnreadNotificationsCount(
	userId?: string,
	accessToken?: string | null
): Promise<number> {
	try {
		const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
		const res = await fetch(`${API_BASE}/notifications/unread-count${query}`, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) return 0;
		const data = await res.json();
		return data.unread_count || 0;
	} catch (err) {
		return 0;
	}
}

export async function markNotificationRead(
	notificationId: string,
	accessToken?: string | null
): Promise<void> {
	try {
		const res = await fetch(`${API_BASE}/notifications/${encodeURIComponent(notificationId)}/read`, {
			method: 'POST',
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to mark notification as read');
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while updating notification');
	}
}

export async function markAllNotificationsRead(
	userId?: string,
	accessToken?: string | null
): Promise<void> {
	try {
		const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
		const res = await fetch(`${API_BASE}/notifications/read-all${query}`, {
			method: 'POST',
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to mark notifications as read');
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while updating notifications');
	}
}

export async function fetchSupporterProfile(username: string): Promise<SupporterProfile | null> {
	try {
		const res = await fetch(`${API_BASE}/supporters/${encodeURIComponent(username)}`);
		if (!res.ok) throw new Error('Failed to fetch supporter profile');
		return await res.json();
	} catch (err) {
		return null;
	}
}

export async function fetchHistoricalMatches(): Promise<HistoricalMatchSummary[]> {
	try {
		const res = await fetch(`${API_BASE}/analytics/historical/matches`);
		if (!res.ok) throw new Error('Failed to fetch historical matches');
		return await res.json();
	} catch (err) {
		return [];
	}
}

export async function fetchHistoricalMatchDetail(matchId: string): Promise<HistoricalMatchDetail | null> {
	try {
		const res = await fetch(`${API_BASE}/analytics/historical/matches/${matchId}`);
		if (!res.ok) throw new Error('Failed to fetch match detail');
		return await res.json();
	} catch (err) {
		return null;
	}
}

export async function fetchTrendingTags(): Promise<TopicTag[]> {
	try {
		const res = await fetch(`${API_BASE}/terrace/tags`);
		if (!res.ok) throw new Error('Failed to fetch trending tags');
		return await res.json();
	} catch (err) {
		return [];
	}
}


function getLocalFallbackMatches(clubId?: string): Match[] {
	const all: Match[] = [
		{
			id: 'fb-ars-1',
			competition_id: 'PL',
			competition_name: 'Premier League',
			season_id: '2024-2025-PL',
			home_team_id: 'arsenal',
			home_team_name: 'Arsenal FC',
			home_team_crest: 'https://crests.football-data.org/57.png',
			away_team_id: 'wolves',
			away_team_name: 'Wolverhampton Wanderers FC',
			away_team_crest: 'https://crests.football-data.org/76.png',
			matchday: 1,
			utc_date: '2024-08-17T14:00:00Z',
			status: 'FINISHED',
			venue: 'Emirates Stadium',
			home_score: 2,
			away_score: 0,
			winner: 'HOME_TEAM',
			source: 'football-data.org'
		},
		{
			id: 'fb-ars-2',
			competition_id: 'PL',
			competition_name: 'Premier League',
			season_id: '2024-2025-PL',
			home_team_id: 'aston-villa',
			home_team_name: 'Aston Villa FC',
			home_team_crest: 'https://crests.football-data.org/58.png',
			away_team_id: 'arsenal',
			away_team_name: 'Arsenal FC',
			away_team_crest: 'https://crests.football-data.org/57.png',
			matchday: 2,
			utc_date: '2024-08-24T14:00:00Z',
			status: 'FINISHED',
			venue: 'Villa Park',
			home_score: 0,
			away_score: 2,
			winner: 'AWAY_TEAM',
			source: 'football-data.org'
		},
		{
			id: 'fb-ars-3',
			competition_id: 'PL',
			competition_name: 'Premier League',
			season_id: '2024-2025-PL',
			home_team_id: 'arsenal',
			home_team_name: 'Arsenal FC',
			home_team_crest: 'https://crests.football-data.org/57.png',
			away_team_id: 'chelsea',
			away_team_name: 'Chelsea FC',
			away_team_crest: 'https://crests.football-data.org/61.png',
			matchday: 11,
			utc_date: '2024-11-10T16:30:00Z',
			status: 'FINISHED',
			venue: 'Stamford Bridge',
			home_score: 1,
			away_score: 1,
			winner: 'DRAW',
			source: 'football-data.org'
		},
		{
			id: 'fb-ars-4',
			competition_id: 'PL',
			competition_name: 'Premier League',
			season_id: '2024-2025-PL',
			home_team_id: 'arsenal',
			home_team_name: 'Arsenal FC',
			home_team_crest: 'https://crests.football-data.org/57.png',
			away_team_id: 'nottingham-forest',
			away_team_name: 'Nottingham Forest FC',
			away_team_crest: 'https://crests.football-data.org/351.png',
			matchday: 12,
			utc_date: new Date(Date.now() + 3 * 86400000).toISOString(),
			status: 'SCHEDULED',
			venue: 'Emirates Stadium',
			source: 'football-data.org'
		}
	];

	if (clubId) {
		return all.filter((m) => m.home_team_id === clubId || m.away_team_id === clubId);
	}
	return all;
}

export async function fetchFormationPresets(): Promise<FormationPreset[]> {
	try {
		const res = await fetch(`${API_BASE}/tactics/formations/presets`);
		if (!res.ok) throw new Error('Failed to fetch formation presets');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching presets, returning local default presets');
		return [
			{
				id: '4-3-3',
				name: '4-3-3 Attacking',
				description: 'High press with aggressive wingers and a single holding midfielder.',
				players: [
					{ id: 'p1', name: 'Raya', number: 1, role: 'GK', x: 5.0, y: 50.0 },
					{ id: 'p2', name: 'Calafiori', number: 33, role: 'LB', x: 24.0, y: 14.0 },
					{ id: 'p3', name: 'Gabriel', number: 6, role: 'CB', x: 20.0, y: 36.0 },
					{ id: 'p4', name: 'Saliba', number: 2, role: 'CB', x: 20.0, y: 64.0 },
					{ id: 'p5', name: 'White', number: 4, role: 'RB', x: 24.0, y: 86.0 },
					{ id: 'p6', name: 'Rice', number: 41, role: 'DM', x: 38.0, y: 50.0 },
					{ id: 'p7', name: 'Merino', number: 23, role: 'CM', x: 54.0, y: 30.0 },
					{ id: 'p8', name: 'Ødegaard', number: 8, role: 'CM', x: 54.0, y: 70.0 },
					{ id: 'p9', name: 'Martinelli', number: 11, role: 'LW', x: 76.0, y: 16.0 },
					{ id: 'p10', name: 'Havertz', number: 29, role: 'ST', x: 82.0, y: 50.0 },
					{ id: 'p11', name: 'Saka', number: 7, role: 'RW', x: 76.0, y: 84.0 }
				]
			},
			{
				id: '4-2-3-1',
				name: '4-2-3-1 Double Pivot',
				description: 'Controlled midfield with a double pivot and a central playmaker.',
				players: [
					{ id: 'p1', name: 'Goalkeeper', number: 1, role: 'GK', x: 5.0, y: 50.0 },
					{ id: 'p2', name: 'Left Back', number: 3, role: 'LB', x: 24.0, y: 14.0 },
					{ id: 'p3', name: 'Left CB', number: 6, role: 'CB', x: 20.0, y: 36.0 },
					{ id: 'p4', name: 'Right CB', number: 2, role: 'CB', x: 20.0, y: 64.0 },
					{ id: 'p5', name: 'Right Back', number: 4, role: 'RB', x: 24.0, y: 86.0 },
					{ id: 'p6', name: 'Pivot 1', number: 41, role: 'DM', x: 38.0, y: 35.0 },
					{ id: 'p7', name: 'Pivot 2', number: 5, role: 'DM', x: 38.0, y: 65.0 },
					{ id: 'p8', name: 'Attacking Mid', number: 8, role: 'AM', x: 58.0, y: 50.0 },
					{ id: 'p9', name: 'Left Wing', number: 11, role: 'LW', x: 72.0, y: 18.0 },
					{ id: 'p10', name: 'Right Wing', number: 7, role: 'RW', x: 72.0, y: 82.0 },
					{ id: 'p11', name: 'Striker', number: 9, role: 'ST', x: 84.0, y: 50.0 }
				]
			}
		];
	}
}

export async function saveTacticalBoard(
	payload: TacticalBoardCreatePayload,
	accessToken?: string | null
): Promise<TacticalBoard> {
	try {
		const res = await fetch(`${API_BASE}/tactics`, {
			method: 'POST',
			headers: buildHeaders(accessToken, { 'Content-Type': 'application/json' }),
			body: JSON.stringify(payload)
		});
		if (!res.ok) await throwApiError(res, 'Failed to publish tactical board');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while publishing tactical board');
	}
}

export async function fetchTacticalBoards(
	clubId?: string,
	accessToken?: string | null
): Promise<TacticalBoard[]> {
	try {
		const url = clubId ? `${API_BASE}/tactics?club_id=${encodeURIComponent(clubId)}` : `${API_BASE}/tactics`;
		const res = await fetchWithTimeout(url, {
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) throw new Error('Failed to fetch tactical boards');
		return await res.json();
	} catch (err) {
		return [];
	}
}

export async function deleteTacticalBoard(
	boardId: string,
	accessToken?: string | null
): Promise<{ status?: string; id?: string }> {
	try {
		const res = await fetchWithTimeout(`${API_BASE}/tactics/${encodeURIComponent(boardId)}`, {
			method: 'DELETE',
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to delete tactical board');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while deleting tactical board');
	}
}

export async function deleteInsight(
	insightId: string,
	accessToken?: string | null
): Promise<{ status?: string; id?: string }> {
	try {
		const res = await fetchWithTimeout(`${API_BASE}/insights/${encodeURIComponent(insightId)}`, {
			method: 'DELETE',
			headers: buildHeaders(accessToken)
		});
		if (!res.ok) await throwApiError(res, 'Failed to delete insight');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while deleting insight');
	}
}

export async function fetchTacticalBoard(boardId: string): Promise<TacticalBoard | null> {
	try {
		const res = await fetch(`${API_BASE}/tactics/${encodeURIComponent(boardId)}`);
		if (!res.ok) throw new Error('Failed to fetch board');
		return await res.json();
	} catch (err) {
		return null;
	}
}

export interface FetchNewsOptions {
	limit?: number;
	offset?: number;
	category?: string;
	tag?: string;
	search?: string;
	refresh?: boolean;
}

export async function fetchArsenalNews(
	optsOrCategory?: FetchNewsOptions | string,
	legacyRefresh: boolean = false
): Promise<NewsFeed> {
	const opts: FetchNewsOptions =
		typeof optsOrCategory === 'string'
			? { category: optsOrCategory, refresh: legacyRefresh }
			: (optsOrCategory ?? {});
	try {
		const params = new URLSearchParams();
		if (opts.limit !== undefined) params.set('limit', String(opts.limit));
		if (opts.offset !== undefined) params.set('offset', String(opts.offset));
		if (opts.category && opts.category !== 'all') params.set('category', opts.category);
		if (opts.tag && opts.tag !== 'all') params.set('tag', opts.tag);
		if (opts.search && opts.search.trim()) params.set('search', opts.search.trim());
		if (opts.refresh) params.set('refresh', 'true');
		const qs = params.toString();
		const url = qs ? `${API_BASE}/news?${qs}` : `${API_BASE}/news`;
		const res = await fetch(url);
		if (!res.ok) throw new Error('Failed to fetch Arsenal news');
		const data = (await res.json()) as NewsFeed;
		return {
			...data,
			has_more: Boolean(data.has_more)
		};
	} catch (err) {
		console.warn('API error fetching Arsenal news, returning baseline feed');
		return {
			total: 3,
			has_more: false,
			sources_active: ['Pain in the Arsenal', 'Arseblog News', 'BBC Sport Arsenal'],
			cached_at: new Date().toISOString(),
			articles: [
				{
					id: 'art_fb_1',
					title: "Arsenal tactical evolution: How Mikel Arteta created European-elite defensive compactness",
					summary: "Deep dive into Arsenal's defensive structure, double pivot spacing, and pressing triggers at Emirates Stadium.",
					source_name: 'Arseblog News',
					source_category: 'fan_blog',
					source_color: '#D4AF37',
					article_url: 'https://arseblog.news',
					image_url: 'https://crests.football-data.org/57.png',
					published_at: new Date().toISOString(),
					author: 'Tactical Analyst'
				},
				{
					id: 'art_fb_2',
					title: "Why Bukayo Saka's half-space combinations unlock stubborn 5-man low blocks",
					summary: 'Analyzing the right-sided triangles between Ben White, Martin Ødegaard, and Bukayo Saka.',
					source_name: 'Pain in the Arsenal',
					source_category: 'fan_blog',
					source_color: '#EF0107',
					article_url: 'https://paininthearsenal.com',
					image_url: 'https://crests.football-data.org/57.png',
					published_at: new Date().toISOString(),
					author: 'Arsenal Staff'
				},
				{
					id: 'art_fb_3',
					title: 'Match Preview: Crucial Premier League clash at Emirates Stadium this weekend',
					summary: 'Team news, predicted starting lineups, head-to-head records, and press conference quotes.',
					source_name: 'BBC Sport Arsenal',
					source_category: 'broadcast',
					source_color: '#FFD700',
					article_url: 'https://www.bbc.com/sport/football/teams/arsenal',
					image_url: 'https://crests.football-data.org/57.png',
					published_at: new Date().toISOString(),
					author: 'BBC Sport'
				}
			]
		};
	}
}

export function getApiErrorMessage(err: unknown, fallback: string): { detail: string; status: number } {
	const apiErr = toNetworkApiError(err, fallback);
	return { detail: apiErr.detail || fallback, status: apiErr.status };
}

export async function fetchMatchDetailStrict(
	matchId: string,
	fetchFn: typeof fetch = fetch
): Promise<Match | null> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/matches/${encodeURIComponent(matchId)}`,
			{},
			15000,
			fetchFn
		);
		if (res.status === 404) return null;
		if (!res.ok) await throwApiError(res, `Failed to load match dossier (${res.status})`);
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach Arsenal match service');
	}
}

export async function fetchPlayerStrict(
	playerId: string,
	fetchFn: typeof fetch = fetch
): Promise<Player | null> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/squad/${encodeURIComponent(playerId)}`,
			{},
			15000,
			fetchFn
		);
		if (res.status === 404) return null;
		if (!res.ok) await throwApiError(res, `Failed to load player dossier (${res.status})`);
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach Arsenal squad service');
	}
}

export async function comparePlayersStrict(
	player1Id: string,
	player2Id: string,
	fetchFn: typeof fetch = fetch
): Promise<PlayerComparison> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/squad/compare?player1_id=${encodeURIComponent(player1Id)}&player2_id=${encodeURIComponent(player2Id)}`,
			{},
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, 'Unable to compare the selected players');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach squad comparison service');
	}
}

export async function fetchMatchesResult(
	params?: {
		club_id?: string;
		competition_id?: string;
		season_id?: string;
		status?: string;
		order?: string;
		limit?: number;
	},
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<Match[]>> {
	try {
		const query = new URLSearchParams();
		if (params?.club_id) query.set('club_id', params.club_id);
		if (params?.competition_id) query.set('competition_id', params.competition_id);
		if (params?.season_id) query.set('season_id', params.season_id);
		if (params?.status) query.set('status', params.status);
		if (params?.order) query.set('order', params.order);
		if (params?.limit) query.set('limit', params.limit.toString());

		const res = await fetchWithTimeout(`${API_BASE}/matches?${query.toString()}`, {}, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, `Failed to fetch matches (${res.status})`);
		const data = (await res.json()) as Match[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load match ledger from backend service.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchMatchSummaryResult(
	clubId: string,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<MatchSummary | null>> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/matches/summary?club_id=${encodeURIComponent(clubId)}`,
			{},
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, `Failed to load match summary (${res.status})`);
		const data = (await res.json()) as MatchSummary;
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load live matchday summary.');
		return { data: null, error: detail, status, isFallback: false };
	}
}

export async function fetchSquadResult(
	clubId?: string,
	position?: string,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<Player[]>> {
	try {
		const query = new URLSearchParams();
		if (clubId) query.set('club_id', clubId);
		if (position) query.set('position', position);
		const res = await fetchWithTimeout(`${API_BASE}/squad?${query.toString()}`, {}, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, `Failed to load squad (${res.status})`);
		const data = (await res.json()) as Player[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load Arsenal squad directory.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchArsenalNewsResult(
	optsOrCategory?: FetchNewsOptions | string,
	legacyRefresh = false,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<NewsFeed>> {
	const opts: FetchNewsOptions =
		typeof optsOrCategory === 'string'
			? { category: optsOrCategory, refresh: legacyRefresh }
			: (optsOrCategory ?? {});
	try {
		const params = new URLSearchParams();
		if (opts.limit !== undefined) params.set('limit', String(opts.limit));
		if (opts.offset !== undefined) params.set('offset', String(opts.offset));
		if (opts.category && opts.category !== 'all') params.set('category', opts.category);
		if (opts.tag && opts.tag !== 'all') params.set('tag', opts.tag);
		if (opts.search && opts.search.trim()) params.set('search', opts.search.trim());
		if (opts.refresh) params.set('refresh', 'true');
		const qs = params.toString();
		const url = qs ? `${API_BASE}/news?${qs}` : `${API_BASE}/news`;
		const res = await fetchWithTimeout(url, {}, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, `Failed to load Arsenal news wire (${res.status})`);
		const payload = (await res.json()) as NewsFeed;
		return {
			data: { ...payload, has_more: Boolean(payload.has_more) },
			error: null,
			status: res.status,
			isFallback: false
		};
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to reach The Armory news wire.');
		return {
			data: {
				total: 0,
				has_more: false,
				sources_active: [],
				cached_at: '',
				articles: []
			},
			error: detail,
			status,
			isFallback: false
		};
	}
}

export async function fetchUpcomingPredictionsStrict(
	userId?: string,
	accessToken?: string | null,
	fetchFn: typeof fetch = fetch
): Promise<UpcomingMatchPrediction[]> {
	try {
		const url = userId
			? `${API_BASE}/predictions/upcoming?user_id=${encodeURIComponent(userId)}`
			: `${API_BASE}/predictions/upcoming`;
		const res = await fetchWithTimeout(url, { headers: buildHeaders(accessToken) }, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, 'Failed to load upcoming fixtures for prediction');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach matchday predictor service');
	}
}

export async function fetchLeaderboardStrict(
	clubId?: string,
	seasonId?: string,
	signal?: AbortSignal,
	fetchFn: typeof fetch = fetch
): Promise<LeaderboardEntry[]> {
	try {
		const query = new URLSearchParams();
		if (clubId) query.set('club_id', clubId);
		if (seasonId && seasonId !== 'all') query.set('season_id', seasonId);
		const qs = query.toString();
		const url = qs ? `${API_BASE}/predictions/leaderboard?${qs}` : `${API_BASE}/predictions/leaderboard`;
		const res = await fetchWithTimeout(url, { signal }, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, 'Failed to load predictor leaderboard');
		return await res.json();
	} catch (err) {
		if (err instanceof DOMException && err.name === 'AbortError') throw err;
		throw toNetworkApiError(err, 'Unable to reach predictor leaderboard service');
	}
}

export async function queryAnalyticsStrict(
	params: {
		metric: string;
		team_ids: string[];
		venue?: string;
		season_id?: string;
	},
	fetchFn: typeof fetch = fetch
): Promise<AnalyticsResponse> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/matches/query`,
			{
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					metric: params.metric,
					team_ids: params.team_ids,
					venue: params.venue || 'all',
					season_id: params.season_id
				})
			},
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, 'Analytics query failed');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach Data Lab analytics engine');
	}
}

export async function fetchMultiSeasonTrendsStrict(
	clubId = 'arsenal',
	venue = 'all',
	fetchFn: typeof fetch = fetch
): Promise<MultiSeasonTrendsResponse> {
	try {
		const query = new URLSearchParams();
		if (clubId) query.set('club_id', clubId);
		if (venue) query.set('venue', venue);
		const res = await fetchWithTimeout(
			`${API_BASE}/matches/trends?${query.toString()}`,
			{},
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, 'Failed to load multi-season trends');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach multi-season trends service');
	}
}

export async function fetchOpponentH2HStrict(
	opponentId: string,
	clubId = 'arsenal',
	venue = 'all',
	fetchFn: typeof fetch = fetch
): Promise<OpponentH2HResponse> {
	try {
		const query = new URLSearchParams();
		query.set('opponent_id', opponentId);
		if (clubId) query.set('club_id', clubId);
		if (venue) query.set('venue', venue);
		const res = await fetchWithTimeout(
			`${API_BASE}/matches/h2h?${query.toString()}`,
			{},
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, 'Failed to load opponent head-to-head record');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach opponent head-to-head service');
	}
}

export async function fetchInsightsResult(
	clubId?: string,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<Insight[]>> {
	try {
		const url = clubId
			? `${API_BASE}/insights?club_id=${encodeURIComponent(clubId)}`
			: `${API_BASE}/insights`;
		const res = await fetchWithTimeout(url, {}, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, `Failed to load insights (${res.status})`);
		const data = (await res.json()) as Insight[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load saved insights.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchTacticalBoardsResult(
	clubId?: string,
	accessToken?: string | null,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<TacticalBoard[]>> {
	try {
		const url = clubId
			? `${API_BASE}/tactics?club_id=${encodeURIComponent(clubId)}`
			: `${API_BASE}/tactics`;
		const res = await fetchWithTimeout(url, { headers: buildHeaders(accessToken) }, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, `Failed to load tactical boards (${res.status})`);
		const data = (await res.json()) as TacticalBoard[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load community tactical boards.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchHistoricalMatchesResult(
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<HistoricalMatchSummary[]>> {
	try {
		const res = await fetchWithTimeout(`${API_BASE}/analytics/historical/matches`, {}, 15000, fetchFn);
		if (!res.ok) await throwApiError(res, `Failed to load historical matches (${res.status})`);
		const data = (await res.json()) as HistoricalMatchSummary[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load historical StatsBomb matches.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchHistoricalMatchDetailStrict(
	matchId: string,
	fetchFn: typeof fetch = fetch
): Promise<HistoricalMatchDetail | null> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/analytics/historical/matches/${encodeURIComponent(matchId)}`,
			{},
			15000,
			fetchFn
		);
		if (res.status === 404) return null;
		if (!res.ok) await throwApiError(res, `Failed to load historical match detail (${res.status})`);
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to load historical match telemetry');
	}
}

export async function fetchPostsResult(
	clubId?: string,
	currentUserId?: string,
	search?: string,
	tag?: string,
	accessToken?: string | null,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<Post[]>> {
	try {
		const query = new URLSearchParams();
		if (clubId && clubId !== 'global') query.set('club_id', clubId);
		if (currentUserId) query.set('current_user_id', currentUserId);
		if (search) query.set('search', search);
		if (tag) query.set('tag', tag);
		const res = await fetchWithTimeout(
			`${API_BASE}/terrace/posts?${query.toString()}`,
			{ headers: buildHeaders(accessToken) },
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, `Failed to load Terrace feed (${res.status})`);
		const data = (await res.json()) as Post[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load The Terrace feed.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchCommentsStrict(
	postId: string,
	fetchFn: typeof fetch = fetch
): Promise<PostComment[]> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/terrace/posts/${encodeURIComponent(postId)}/comments`,
			{},
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, 'Failed to load replies');
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to reach server while loading replies');
	}
}

export async function fetchConversationsResult(
	userId?: string,
	accessToken?: string | null,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<Conversation[]>> {
	try {
		const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
		const res = await fetchWithTimeout(
			`${API_BASE}/messages/conversations${query}`,
			{ headers: buildHeaders(accessToken) },
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, `Failed to load conversations (${res.status})`);
		const data = (await res.json()) as Conversation[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load debates inbox.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchNotificationsResult(
	userId?: string,
	accessToken?: string | null,
	fetchFn: typeof fetch = fetch
): Promise<ApiResult<Notification[]>> {
	try {
		const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
		const res = await fetchWithTimeout(
			`${API_BASE}/notifications${query}`,
			{ headers: buildHeaders(accessToken) },
			15000,
			fetchFn
		);
		if (!res.ok) await throwApiError(res, `Failed to load notifications (${res.status})`);
		const data = (await res.json()) as Notification[];
		return { data, error: null, status: res.status, isFallback: false };
	} catch (err) {
		const { detail, status } = getApiErrorMessage(err, 'Unable to load notifications.');
		return { data: [], error: detail, status, isFallback: false };
	}
}

export async function fetchSupporterProfileStrict(
	username: string,
	fetchFn: typeof fetch = fetch
): Promise<SupporterProfile | null> {
	try {
		const res = await fetchWithTimeout(
			`${API_BASE}/supporters/${encodeURIComponent(username)}`,
			{},
			15000,
			fetchFn
		);
		if (res.status === 404) return null;
		if (!res.ok) await throwApiError(res, `Failed to load supporter dossier (${res.status})`);
		return await res.json();
	} catch (err) {
		throw toNetworkApiError(err, 'Unable to load supporter profile');
	}
}

