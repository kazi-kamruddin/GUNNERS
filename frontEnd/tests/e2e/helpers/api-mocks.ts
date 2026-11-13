import type { Page, Route } from '@playwright/test';

const TINY_PNG = Buffer.from(
	'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
	'base64'
);

export const SAMPLE_NEWS_ARTICLES = [
	{
		id: 'news_1',
		title: 'Saka leads Arsenal build-up overload against Chelsea',
		summary: 'Right half-space combinations unlocked Chelsea early at Emirates Stadium.',
		source_name: 'Arseblog',
		source_category: 'fan_blog',
		article_url: 'https://arseblog.com/example-saka',
		image_url: 'https://crests.football-data.org/57.png',
		published_at: '2026-11-12T12:00:00Z',
		author: 'Andrew Mangan',
		tags: ['Saka', 'Tactics']
	},
	{
		id: 'news_2',
		title: 'Arteta confirms Calafiori recovery timeline ahead of UCL clash',
		summary: 'Manager outlines defensive rotation options before midweek Champions League action.',
		source_name: 'BBC Sport',
		source_category: 'broadcast',
		article_url: 'https://bbc.co.uk/sport/football/example-arteta',
		image_url: 'https://crests.football-data.org/57.png',
		published_at: '2026-11-11T16:30:00Z',
		author: 'BBC Football',
		tags: ['Arteta', 'UCL']
	}
];

export const SAMPLE_SEASONS = [
	{
		id: '2025-2026-PL',
		label: '2025/26',
		headline: 'Title charge consolidation',
		arteta_milestone: 'High-press maturity and set-piece dominance.',
		is_current: true
	},
	{
		id: '2024-2025-PL',
		label: '2024/25',
		headline: 'Champions League semi-finalists',
		arteta_milestone: 'Defensive structure and squad depth breakthrough.',
		is_current: false
	}
];

export const SAMPLE_MATCHES = [
	{
		id: 'match_1',
		competition_id: 'PL',
		competition_name: 'Premier League',
		season_id: '2025-2026-PL',
		home_team_id: 'arsenal',
		home_team_name: 'Arsenal FC',
		home_team_crest: 'https://crests.football-data.org/57.png',
		away_team_id: 'chelsea',
		away_team_name: 'Chelsea FC',
		away_team_crest: 'https://crests.football-data.org/61.png',
		matchday: 29,
		utc_date: '2026-04-12T15:30:00Z',
		status: 'FINISHED',
		home_score: 3,
		away_score: 1,
		winner: 'HOME_TEAM',
		venue: 'Emirates Stadium',
		referee: 'Michael Oliver',
		source: 'football-data.org',
		goalscorers: [
			{ player: 'Bukayo Saka', minute: 22, team: 'Arsenal FC', type: 'Open Play', assist: 'Martin Ødegaard' },
			{ player: 'Viktor Gyökeres', minute: 68, team: 'Arsenal FC', type: 'Open Play', assist: 'Declan Rice' }
		],
		lineups: {
			home: {
				formation: '4-3-3',
				xi: [
					{ name: 'David Raya', number: 1, position: 'GK' },
					{ name: 'Bukayo Saka', number: 7, position: 'RW' }
				]
			},
			away: {
				formation: '4-2-3-1',
				xi: [{ name: 'Robert Sánchez', number: 1, position: 'GK' }]
			}
		},
		highlights: [{ label: 'Extended Emirates highlights', url: 'https://example.com/highlights', source: 'Arsenal.com' }]
	},
	{
		id: 'match_2',
		competition_id: 'CL',
		competition_name: 'Champions League',
		season_id: '2025-2026-PL',
		home_team_id: 'arsenal',
		home_team_name: 'Arsenal FC',
		home_team_crest: 'https://crests.football-data.org/57.png',
		away_team_id: 'real-madrid',
		away_team_name: 'Real Madrid CF',
		away_team_crest: 'https://crests.football-data.org/86.png',
		matchday: 10,
		utc_date: new Date(Date.now() + 5 * 86400_000).toISOString(),
		status: 'SCHEDULED',
		venue: 'Emirates Stadium',
		source: 'football-data.org'
	}
];

export const SAMPLE_PLAYERS = [
	{
		id: 'ply_saka',
		name: 'Bukayo Saka',
		short_name: 'Saka',
		jersey_number: 7,
		position: 'Attacker',
		nationality: 'England',
		date_of_birth: '2001-09-05',
		height: '178 cm',
		joined_date: '2018-07-01',
		appearances: 30,
		goals: 16,
		assists: 12,
		goal_contributions: 28,
		clean_sheets: 0,
		minutes_played: 2540,
		goals_per_game: 0.53,
		assists_per_game: 0.4,
		yellow_cards: 3,
		red_cards: 0,
		portrait_url: 'https://resources.premierleague.com/saka-portrait.png',
		action_url: 'https://resources.premierleague.com/saka-action.png',
		bio: 'Hale End graduate and right-wing captaincy leader.'
	},
	{
		id: 'ply_rice',
		name: 'Declan Rice',
		short_name: 'Rice',
		jersey_number: 41,
		position: 'Midfielder',
		nationality: 'England',
		date_of_birth: '1999-01-14',
		height: '188 cm',
		joined_date: '2023-07-15',
		appearances: 32,
		goals: 7,
		assists: 9,
		goal_contributions: 16,
		clean_sheets: 0,
		minutes_played: 2810,
		goals_per_game: 0.22,
		assists_per_game: 0.28,
		yellow_cards: 4,
		red_cards: 0,
		portrait_url: 'https://resources.premierleague.com/rice-portrait.png',
		action_url: 'https://resources.premierleague.com/rice-action.png',
		bio: 'Box-to-box engine anchoring Arsenal midfield transitions.'
	},
	{
		id: 'ply_gyokeres',
		name: 'Viktor Gyökeres',
		short_name: 'Gyökeres',
		jersey_number: 14,
		position: 'Attacker',
		nationality: 'Sweden',
		date_of_birth: '1998-06-04',
		height: '189 cm',
		joined_date: '2025-07-01',
		appearances: 28,
		goals: 19,
		assists: 5,
		goal_contributions: 24,
		clean_sheets: 0,
		minutes_played: 2320,
		goals_per_game: 0.68,
		assists_per_game: 0.18,
		yellow_cards: 2,
		red_cards: 0,
		portrait_url: 'https://resources.premierleague.com/gyokeres-portrait.png',
		action_url: 'https://resources.premierleague.com/gyokeres-action.png',
		bio: 'Direct vertical striker pressing the back line.'
	}
];

export const SAMPLE_HISTORICAL_MATCHES = [
	{
		id: 'hist_ars_barca_2011',
		title: 'Arsenal 2-1 Barcelona',
		competition: 'UEFA Champions League',
		season: '2010/11',
		match_date: '2011-02-16',
		home_team_id: 'arsenal',
		home_team_name: 'Arsenal FC',
		away_team_id: 'barcelona',
		away_team_name: 'FC Barcelona',
		home_score: 2,
		away_score: 1,
		venue: 'Emirates Stadium',
		data_provider: 'StatsBomb Open Data',
		license_notice: 'Match telemetry provided under StatsBomb Open Data (ODbL v1.0).'
	}
];

export const SAMPLE_HISTORICAL_DETAIL = {
	id: 'hist_ars_barca_2011',
	title: 'Arsenal 2-1 Barcelona',
	competition: 'UEFA Champions League',
	season: '2010/11',
	match_date: '2011-02-16',
	home_team_id: 'arsenal',
	home_team_name: 'Arsenal FC',
	away_team_id: 'barcelona',
	away_team_name: 'FC Barcelona',
	home_score: 2,
	away_score: 1,
	venue: 'Emirates Stadium',
	data_provider: 'StatsBomb Open Data',
	license_notice: 'Match telemetry provided under StatsBomb Open Data (ODbL v1.0).',
	total_xg_home: 1.84,
	total_xg_away: 1.42,
	total_shots_home: 2,
	total_shots_away: 1,
	shots: [
		{
			id: 'shot_1',
			team_id: 'arsenal',
			team_name: 'Arsenal FC',
			player_name: 'Robin van Persie',
			minute: 78,
			second: 14,
			x: 92,
			y: 35,
			xg: 0.24,
			outcome: 'Goal',
			body_part: 'Left Foot',
			shot_type: 'Open Play'
		},
		{
			id: 'shot_2',
			team_id: 'arsenal',
			team_name: 'Arsenal FC',
			player_name: 'Andrey Arshavin',
			minute: 83,
			second: 41,
			x: 88,
			y: 52,
			xg: 0.38,
			outcome: 'Goal',
			body_part: 'Right Foot',
			shot_type: 'Open Play'
		},
		{
			id: 'shot_3',
			team_id: 'barcelona',
			team_name: 'FC Barcelona',
			player_name: 'David Villa',
			minute: 26,
			second: 9,
			x: 89,
			y: 44,
			xg: 0.31,
			outcome: 'Goal',
			body_part: 'Left Foot',
			shot_type: 'Open Play'
		}
	],
	pass_nodes: [
		{
			player_name: 'Cesc Fàbregas',
			position: 'CM',
			jersey_number: 4,
			x: 56,
			y: 48,
			passes_completed: 54
		},
		{
			player_name: 'Samir Nasri',
			position: 'LW',
			jersey_number: 8,
			x: 72,
			y: 26,
			passes_completed: 41
		}
	],
	pass_links: [
		{
			source: 'Cesc Fàbregas',
			target: 'Samir Nasri',
			pass_count: 14
		}
	]
};

export interface MockApiOptions {
	newsOverride?: (url: URL, route: Route) => Promise<void> | void;
	matchDetailOverride?: (matchId: string, route: Route) => Promise<void> | void;
	tacticsPostOverride?: (route: Route) => Promise<void> | void;
	upcomingOverride?: (route: Route) => Promise<void> | void;
	terracePosts?: Array<Record<string, unknown>>;
}

export async function installApiMocks(page: Page, opts: MockApiOptions = {}): Promise<void> {
	// Stub external crests/avatars cleanly so offline/sandboxed CI emits zero image network console errors.
	await page.route('https://crests.football-data.org/**', (route) =>
		route.fulfill({ status: 200, contentType: 'image/png', body: TINY_PNG })
	);
	await page.route('https://resources.premierleague.com/**', (route) =>
		route.fulfill({ status: 200, contentType: 'image/png', body: TINY_PNG })
	);

	await page.route('**/api/v1/**', async (route) => {
		const req = route.request();
		const url = new URL(req.url());
		const path = url.pathname;
		const method = req.method().toUpperCase();

		if (path.endsWith('/news')) {
			if (opts.newsOverride) {
				await opts.newsOverride(url, route);
				return;
			}
			const category = url.searchParams.get('category');
			const tag = url.searchParams.get('tag');
			const search = url.searchParams.get('search')?.toLowerCase() ?? '';
			let filtered = SAMPLE_NEWS_ARTICLES;
			if (category && category !== 'all') {
				filtered = filtered.filter((a) => a.source_category === category);
			}
			if (tag && tag !== 'all') {
				filtered = filtered.filter((a) => a.tags.includes(tag));
			}
			if (search) {
				filtered = filtered.filter(
					(a) => a.title.toLowerCase().includes(search) || a.summary.toLowerCase().includes(search)
				);
			}
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					total: filtered.length,
					has_more: false,
					sources_active: ['Arseblog', 'BBC Sport'],
					cached_at: '2026-11-12T12:00:00Z',
					articles: filtered
				})
			});
			return;
		}

		if (path.endsWith('/matches/summary')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					club_id: 'arsenal',
					club_name: 'ARSENAL',
					next_fixture: SAMPLE_MATCHES[1],
					last_result: SAMPLE_MATCHES[0],
					recent_form: ['W', 'W', 'D', 'W', 'W'],
					total_completed: 28,
					total_scheduled: 10
				})
			});
			return;
		}

		if (path.endsWith('/matches/seasons')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(SAMPLE_SEASONS)
			});
			return;
		}

		if (path.endsWith('/matches/sync-status')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					source: 'football-data.org',
					latest_sync: '2026-11-12T10:00:00Z'
				})
			});
			return;
		}

		if (path.endsWith('/matches/query')) {
			const body = req.postDataJSON?.() ?? { metric: 'win_rate', team_ids: ['arsenal'], venue: 'all' };
			const metric = String(body.metric || 'win_rate');
			const venue = String(body.venue || 'all');
			const teamIds: string[] = Array.isArray(body.team_ids) && body.team_ids.length ? body.team_ids : ['arsenal'];
			const unit = metric === 'win_rate' || metric === 'clean_sheet_rate' ? '%' : metric === 'points_per_game' ? 'pts/g' : 'g/m';
			const metricValue = metric === 'win_rate' ? 68.4 : 2.15;
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					metric,
					formula: 'Aggregated across completed fixtures in PostgreSQL',
					venue_filter: venue,
					computed_at: '2026-11-12T12:00:00Z',
					disclaimer: 'Computed from verified PostgreSQL match records.',
					series: teamIds.map((tid) => ({
						team_id: tid,
						team_name: tid === 'arsenal' ? 'Arsenal FC' : 'Real Madrid CF',
						metric_value: metricValue,
						unit,
						matches_played: 38,
						wins: 26,
						draws: 7,
						losses: 5,
						clean_sheets: 17,
						goals_for: 82,
						goals_against: 29,
						goal_difference: 53
					}))
				})
			});
			return;
		}

		if (path.endsWith('/matches/trends')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					club_id: 'arsenal',
					club_name: 'Arsenal FC',
					venue_filter: url.searchParams.get('venue') || 'all',
					computed_at: '2026-11-12T12:00:00Z',
					trends: [
						{
							season_id: '2024-2025-PL',
							label: '2024/25',
							start_year: 2024,
							end_year: 2025,
							matches_played: 38,
							wins: 24,
							draws: 8,
							losses: 6,
							clean_sheets: 17,
							goals_for: 78,
							goals_against: 31,
							goal_difference: 47,
							win_rate: 63.2,
							points_per_game: 2.1,
							goals_per_match: 2.05,
							clean_sheet_rate: 44.7,
							loss_rate: 15.8,
							arteta_milestone: 'Title contenders'
						},
						{
							season_id: '2025-2026-PL',
							label: '2025/26',
							start_year: 2025,
							end_year: 2026,
							matches_played: 30,
							wins: 21,
							draws: 6,
							losses: 3,
							clean_sheets: 15,
							goals_for: 68,
							goals_against: 21,
							goal_difference: 47,
							win_rate: 70.0,
							points_per_game: 2.3,
							goals_per_match: 2.27,
							clean_sheet_rate: 50.0,
							loss_rate: 10.0,
							arteta_milestone: 'Current campaign'
						}
					]
				})
			});
			return;
		}

		if (path.endsWith('/matches/h2h')) {
			const opp = url.searchParams.get('opponent_id') || 'chelsea';
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					club_id: 'arsenal',
					opponent_id: opp,
					opponent_name: opp === 'chelsea' ? 'Chelsea FC' : 'Tottenham Hotspur FC',
					venue_filter: url.searchParams.get('venue') || 'all',
					matches_played: 6,
					wins: 4,
					draws: 2,
					losses: 0,
					goals_for: 14,
					goals_against: 5,
					recent_matches: [SAMPLE_MATCHES[0]]
				})
			});
			return;
		}

		if (path.endsWith('/api/v1/matches')) {
			const comp = url.searchParams.get('competition_id');
			const status = url.searchParams.get('status');
			const season = url.searchParams.get('season_id');
			let list = SAMPLE_MATCHES;
			if (comp && comp !== 'ALL') list = list.filter((m) => m.competition_id === comp);
			if (status && status !== 'ALL') list = list.filter((m) => m.status === status);
			if (season && season !== 'all') list = list.filter((m) => m.season_id === season);
			await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(list) });
			return;
		}

		if (/\/api\/v1\/matches\/[^/]+$/.test(path)) {
			const matchId = decodeURIComponent(path.split('/').pop() || '');
			if (opts.matchDetailOverride) {
				await opts.matchDetailOverride(matchId, route);
				return;
			}
			const found = SAMPLE_MATCHES.find((m) => m.id === matchId);
			if (!found) {
				await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'Match dossier not found' }) });
				return;
			}
			await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(found) });
			return;
		}

		if (path.endsWith('/squad/compare')) {
			const p1Id = url.searchParams.get('player1_id') || 'ply_saka';
			const p2Id = url.searchParams.get('player2_id') || 'ply_gyokeres';
			const p1 = SAMPLE_PLAYERS.find((p) => p.id === p1Id) || SAMPLE_PLAYERS[0];
			const p2 = SAMPLE_PLAYERS.find((p) => p.id === p2Id) || SAMPLE_PLAYERS[2];
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					player1: {
						player: p1,
						goals_per_90: 0.57,
						assists_per_90: 0.42,
						minutes_per_contribution: 90.7,
						discipline_score: 8.5
					},
					player2: {
						player: p2,
						goals_per_90: 0.74,
						assists_per_90: 0.19,
						minutes_per_contribution: 96.7,
						discipline_score: 9.0
					},
					comparison_summary: `${p1.short_name} creates more assists while ${p2.short_name} leads goals per 90.`
				})
			});
			return;
		}

		if (path.endsWith('/squad')) {
			const pos = url.searchParams.get('position');
			const list = pos ? SAMPLE_PLAYERS.filter((p) => p.position === pos) : SAMPLE_PLAYERS;
			await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(list) });
			return;
		}

		if (/\/squad\/[^/]+$/.test(path)) {
			const pid = decodeURIComponent(path.split('/').pop() || '');
			const found = SAMPLE_PLAYERS.find((p) => p.id === pid);
			if (!found) {
				await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'Player not found' }) });
				return;
			}
			await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(found) });
			return;
		}

		if (path.endsWith('/tactics/formations/presets')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						id: '4-3-3',
						name: '4-3-3 Attacking',
						description: 'High press with inverted full-backs.',
						players: [
							{ id: 'p1', name: 'Raya', number: 1, role: 'GK', x: 5, y: 50 },
							{ id: 'p2', name: 'Calafiori', number: 33, role: 'LB', x: 24, y: 14 },
							{ id: 'p3', name: 'Gabriel', number: 6, role: 'CB', x: 20, y: 36 },
							{ id: 'p4', name: 'Saliba', number: 2, role: 'CB', x: 20, y: 64 },
							{ id: 'p5', name: 'White', number: 4, role: 'RB', x: 24, y: 86 },
							{ id: 'p6', name: 'Rice', number: 41, role: 'DM', x: 38, y: 50 },
							{ id: 'p7', name: 'Merino', number: 23, role: 'CM', x: 54, y: 30 },
							{ id: 'p8', name: 'Ødegaard', number: 8, role: 'CM', x: 54, y: 70 },
							{ id: 'p9', name: 'Martinelli', number: 11, role: 'LW', x: 76, y: 16 },
							{ id: 'p10', name: 'Havertz', number: 29, role: 'ST', x: 82, y: 50 },
							{ id: 'p11', name: 'Saka', number: 7, role: 'RW', x: 76, y: 84 }
						]
					}
				])
			});
			return;
		}

		if (path.endsWith('/tactics')) {
			if (method === 'POST') {
				if (opts.tacticsPostOverride) {
					await opts.tacticsPostOverride(route);
					return;
				}
				await route.fulfill({
					status: 401,
					contentType: 'application/json',
					body: JSON.stringify({ detail: 'Authentication required' })
				});
				return;
			}
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						id: 'board_1',
						user_id: 'owner_user_1',
						author_name: 'ArtetaAnalyst',
						title: 'High-press asymmetrical 4-3-3',
						formation: '4-3-3 Attacking',
						tactical_notes: 'Lock left channel with Calafiori inverting beside Rice.',
						lineup: [{ id: 'p1', name: 'Raya', number: 1, role: 'GK', x: 5, y: 50 }],
						annotations: []
					}
				])
			});
			return;
		}

		if (path.endsWith('/insights')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						id: 'ins_1',
						title: 'Emirates home win benchmark',
						metric: 'win_rate',
						team_ids: ['arsenal'],
						venue: 'home',
						chart_type: 'bar',
						author_name: 'GoonerLab',
						author_club_id: 'arsenal',
						is_public: true,
						created_at: '2026-11-10T10:00:00Z',
						snapshot: { metric: 'win_rate', venue_filter: 'home', series: [] }
					}
				])
			});
			return;
		}

		if (path.endsWith('/analytics/historical/matches')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(SAMPLE_HISTORICAL_MATCHES)
			});
			return;
		}

		if (/\/analytics\/historical\/matches\/[^/]+$/.test(path)) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(SAMPLE_HISTORICAL_DETAIL)
			});
			return;
		}

		if (path.endsWith('/predictions/upcoming')) {
			if (opts.upcomingOverride) {
				await opts.upcomingOverride(route);
				return;
			}
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						match: SAMPLE_MATCHES[1],
						can_predict: true,
						user_prediction: null,
						total_predictions_count: 142
					},
					{
						match: {
							...SAMPLE_MATCHES[0],
							id: 'match_locked',
							utc_date: '2025-01-10T15:00:00Z',
							status: 'SCHEDULED'
						},
						can_predict: false,
						user_prediction: null,
						total_predictions_count: 89
					}
				])
			});
			return;
		}

		if (path.endsWith('/predictions/leaderboard')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						rank: 1,
						user_id: 'u1',
						user_name: 'HighburyOracle',
						user_club_id: 'arsenal',
						total_points: 27,
						exact_hits: 6,
						outcomes_correct: 9
					}
				])
			});
			return;
		}

		if (path.endsWith('/terrace/posts')) {
			const posts = opts.terracePosts ?? [
				{
					id: 'post_1',
					author_id: 'u1',
					author_name: 'ClockEndAnalyst',
					author_club_id: 'arsenal',
					content: 'Saka and Ødegaard dominated the right channel all evening. #Saka #Tactics',
					created_at: '2026-11-12T09:00:00Z',
					reactions_count: 14,
					comments_count: 3,
					user_reacted: false
				}
			];
			await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(posts) });
			return;
		}

		if (path.endsWith('/terrace/trending-tags')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{ tag: 'Saka', count: 12 },
					{ tag: 'Tactics', count: 8 }
				])
			});
			return;
		}

		if (path.endsWith('/clubs')) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{ id: 'arsenal', name: 'Arsenal FC', short_name: 'ARS' },
					{ id: 'man-city', name: 'Manchester City FC', short_name: 'MCI' }
				])
			});
			return;
		}

		await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
	});
}

/**
 * Triggers SvelteKit client-side navigation from an already-hydrated page so universal
 * `+page.ts` load() calls run in the browser and hit `page.route` API mocks.
 */
export async function navigateSpa(page: Page, targetPath: string): Promise<void> {
	const cleanTarget = targetPath.startsWith('/') ? targetPath : `/${targetPath}`;
	await page.evaluate((href) => {
		const link = document.createElement('a');
		link.href = href;
		link.style.position = 'fixed';
		link.style.top = '0';
		link.style.left = '0';
		link.style.opacity = '0.01';
		link.dataset.pwSpaLink = 'true';
		document.body.appendChild(link);
		link.click();
		link.remove();
	}, cleanTarget);
	const expectedPath = cleanTarget.split('?')[0].split('#')[0];
	await page.waitForFunction(
		(exp) => window.location.pathname === exp,
		expectedPath,
		{ timeout: 10_000 }
	);
}

