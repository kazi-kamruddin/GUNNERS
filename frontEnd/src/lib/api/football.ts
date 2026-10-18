import type { Club, AnalyticsResponse } from '$lib/types/football';

const API_BASE = 'http://localhost:8000/api/v1';

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
				accent_color: '#9C824A'
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
				accent_color: '#EEB028'
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
				accent_color: '#EDBB00'
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
				accent_color: '#C0C0C0'
			}
		];
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
