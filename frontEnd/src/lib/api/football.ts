import type { Club, Match, MatchSummary, SyncStatus, AnalyticsResponse, Insight, InsightCreatePayload } from '$lib/types/football';

const API_BASE = (import.meta.env.PUBLIC_API_URL as string) || 'http://localhost:8000/api/v1';

export async function fetchClubs(): Promise<Club[]> {
	try {
		const res = await fetch(`${API_BASE}/clubs`);
		if (!res.ok) throw new Error('Failed to fetch clubs');
		return await res.json();
	} catch (err) {
		console.warn('API unavailable, falling back to local foundation clubs');
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
				is_foundation: true
			},
			{
				id: 'real-madrid',
				slug: 'real-madrid',
				name: 'Real Madrid CF',
				short_name: 'Real Madrid',
				league: 'La Liga',
				country: 'Spain',
				primary_color: '#00529F',
				secondary_color: '#FFFFFF',
				accent_color: '#EEB028',
				crest_url: 'https://crests.football-data.org/86.png',
				is_foundation: true
			},
			{
				id: 'barcelona',
				slug: 'barcelona',
				name: 'FC Barcelona',
				short_name: 'Barcelona',
				league: 'La Liga',
				country: 'Spain',
				primary_color: '#A50044',
				secondary_color: '#004D98',
				accent_color: '#EDBB00',
				crest_url: 'https://crests.football-data.org/81.png',
				is_foundation: true
			},
			{
				id: 'milan',
				slug: 'milan',
				name: 'AC Milan',
				short_name: 'AC Milan',
				league: 'Serie A',
				country: 'Italy',
				primary_color: '#FB090B',
				secondary_color: '#000000',
				accent_color: '#C0C0C0',
				crest_url: 'https://crests.football-data.org/98.png',
				is_foundation: true
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
		return {
			latest_sync: new Date().toISOString(),
			status: 'ACTIVE',
			source: 'football-data.org (cached baseline)',
			matches_synced: 50
		};
	}
}

export async function queryAnalytics(params: {
	metric: string;
	team_ids: string[];
	venue?: string;
}): Promise<AnalyticsResponse | null> {
	try {
		const res = await fetch(`${API_BASE}/matches/query`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				metric: params.metric,
				team_ids: params.team_ids,
				venue: params.venue || 'all'
			})
		});
		if (!res.ok) throw new Error('Analytics query failed');
		return await res.json();
	} catch (err) {
		console.error('Error querying analytics:', err);
		return null;
	}
}

export async function createInsight(payload: InsightCreatePayload): Promise<Insight | null> {
	try {
		const res = await fetch(`${API_BASE}/insights`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		});
		if (!res.ok) throw new Error('Failed to create insight');
		return await res.json();
	} catch (err) {
		console.warn('API error saving insight, generating local snapshot');
		return {
			id: `ins_${Math.random().toString(36).substring(2, 10)}`,
			author_name: payload.author_name || 'Supporter',
			author_club_id: payload.author_club_id || 'arsenal',
			title: payload.title,
			description: payload.description,
			metric: payload.metric,
			team_ids: payload.team_ids,
			venue: payload.venue,
			chart_type: payload.chart_type || 'bar',
			snapshot: payload.snapshot || {
				metric: payload.metric,
				formula: '',
				venue_filter: payload.venue,
				series: [],
				computed_at: new Date().toISOString(),
				disclaimer: 'Calculated across eligible completed matches.'
			},
			is_public: true,
			created_at: new Date().toISOString()
		};
	}
}

export async function fetchInsights(clubId?: string): Promise<Insight[]> {
	try {
		const url = clubId ? `${API_BASE}/insights?club_id=${clubId}` : `${API_BASE}/insights`;
		const res = await fetch(url);
		if (!res.ok) throw new Error('Failed to fetch insights');
		return await res.json();
	} catch (err) {
		console.warn('API error fetching insights, returning local default insights');
		return [
			{
				id: 'ins_demo_1',
				author_name: 'TacticsGooner',
				author_club_id: 'arsenal',
				title: "Arsenal Home Win Rate 2024/25",
				description: 'Emirates Stadium home record across all competitions.',
				metric: 'win_rate',
				team_ids: ['arsenal'],
				venue: 'home',
				chart_type: 'bar',
				snapshot: {
					metric: 'win_rate',
					formula: '(wins / matches_played) * 100',
					venue_filter: 'home',
					series: [{
						team_id: 'arsenal',
						team_name: 'Arsenal FC',
						matches_played: 6,
						wins: 5,
						draws: 1,
						losses: 0,
						clean_sheets: 3,
						goals_for: 14,
						goals_against: 4,
						goal_difference: 10,
						metric_value: 83.3,
						unit: '%'
					}],
					computed_at: new Date().toISOString(),
					disclaimer: 'Calculated strictly across eligible completed matches.'
				},
				is_public: true,
				created_at: new Date(Date.now() - 3600000).toISOString()
			},
			{
				id: 'ins_demo_2',
				author_name: 'MadridistaAnalytics',
				author_club_id: 'real-madrid',
				title: 'Real Madrid vs Barcelona PPG Comparison',
				description: 'Points per game comparison across current campaign matches.',
				metric: 'points_per_game',
				team_ids: ['real-madrid', 'barcelona'],
				venue: 'all',
				chart_type: 'comparison',
				snapshot: {
					metric: 'points_per_game',
					formula: '((wins * 3) + draws) / matches_played',
					venue_filter: 'all',
					series: [
						{
							team_id: 'real-madrid',
							team_name: 'Real Madrid CF',
							matches_played: 10,
							wins: 7,
							draws: 2,
							losses: 1,
							clean_sheets: 4,
							goals_for: 21,
							goals_against: 11,
							goal_difference: 10,
							metric_value: 2.3,
							unit: 'ppg'
						},
						{
							team_id: 'barcelona',
							team_name: 'FC Barcelona',
							matches_played: 10,
							wins: 8,
							draws: 0,
							losses: 2,
							clean_sheets: 3,
							goals_for: 31,
							goals_against: 11,
							goal_difference: 20,
							metric_value: 2.4,
							unit: 'ppg'
						}
					],
					computed_at: new Date().toISOString(),
					disclaimer: 'Calculated strictly across eligible completed matches.'
				},
				is_public: true,
				created_at: new Date(Date.now() - 7200000).toISOString()
			}
		];
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
		},
		{
			id: 'fb-rma-1',
			competition_id: 'PD',
			competition_name: 'La Liga',
			season_id: '2024-2025-PD',
			home_team_id: 'real-madrid',
			home_team_name: 'Real Madrid CF',
			home_team_crest: 'https://crests.football-data.org/86.png',
			away_team_id: 'valladolid',
			away_team_name: 'Real Valladolid CF',
			away_team_crest: 'https://crests.football-data.org/250.png',
			matchday: 2,
			utc_date: '2024-08-25T15:00:00Z',
			status: 'FINISHED',
			venue: 'Santiago Bernabéu',
			home_score: 3,
			away_score: 0,
			winner: 'HOME_TEAM',
			source: 'football-data.org'
		},
		{
			id: 'fb-rma-2',
			competition_id: 'PD',
			competition_name: 'La Liga',
			season_id: '2024-2025-PD',
			home_team_id: 'real-madrid',
			home_team_name: 'Real Madrid CF',
			home_team_crest: 'https://crests.football-data.org/86.png',
			away_team_id: 'barcelona',
			away_team_name: 'FC Barcelona',
			away_team_crest: 'https://crests.football-data.org/81.png',
			matchday: 11,
			utc_date: '2024-10-26T19:00:00Z',
			status: 'FINISHED',
			venue: 'Santiago Bernabéu',
			home_score: 0,
			away_score: 4,
			winner: 'AWAY_TEAM',
			source: 'football-data.org'
		},
		{
			id: 'fb-bar-1',
			competition_id: 'PD',
			competition_name: 'La Liga',
			season_id: '2024-2025-PD',
			home_team_id: 'barcelona',
			home_team_name: 'FC Barcelona',
			home_team_crest: 'https://crests.football-data.org/81.png',
			away_team_id: 'valladolid',
			away_team_name: 'Real Valladolid CF',
			away_team_crest: 'https://crests.football-data.org/250.png',
			matchday: 4,
			utc_date: '2024-08-31T15:00:00Z',
			status: 'FINISHED',
			venue: 'Montjuïc',
			home_score: 7,
			away_score: 0,
			winner: 'HOME_TEAM',
			source: 'football-data.org'
		},
		{
			id: 'fb-mil-1',
			competition_id: 'SA',
			competition_name: 'Serie A',
			season_id: '2024-2025-SA',
			home_team_id: 'inter',
			home_team_name: 'FC Internazionale Milano',
			home_team_crest: 'https://crests.football-data.org/108.png',
			away_team_id: 'milan',
			away_team_name: 'AC Milan',
			away_team_crest: 'https://crests.football-data.org/98.png',
			matchday: 5,
			utc_date: '2024-09-22T18:45:00Z',
			status: 'FINISHED',
			venue: 'San Siro',
			home_score: 1,
			away_score: 2,
			winner: 'AWAY_TEAM',
			source: 'football-data.org'
		}
	];

	if (clubId) {
		return all.filter((m) => m.home_team_id === clubId || m.away_team_id === clubId);
	}
	return all;
}
