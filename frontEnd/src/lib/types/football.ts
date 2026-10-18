export interface Club {
	id: string;
	slug: string;
	name: string;
	short_name: string;
	primary_color: string;
	secondary_color: string;
	accent_color: string;
	league: string;
	country: string;
	crest_url?: string;
	is_foundation?: boolean;
}

export interface Match {
	id: string;
	competition_id?: string;
	competition_name?: string;
	season_id: string;
	home_team_id: string;
	home_team_name: string;
	home_team_crest?: string;
	away_team_id: string;
	away_team_name: string;
	away_team_crest?: string;
	matchday?: number;
	utc_date: string;
	status: string;
	venue?: string;
	home_score?: number;
	away_score?: number;
	winner?: string;
	source?: string;
}

export interface MatchSummary {
	club_id: string;
	club_name: string;
	next_fixture?: Match | null;
	last_result?: Match | null;
	recent_form: string[];
	total_completed: number;
	total_scheduled: number;
}

export interface SyncStatus {
	latest_sync?: string;
	status: string;
	source: string;
	matches_synced: number;
	error_message?: string;
}

export interface AnalyticsSeriesItem {
	team_id: string;
	team_name: string;
	matches_played: number;
	wins: number;
	draws: number;
	losses: number;
	clean_sheets?: number;
	goals_for: number;
	goals_against: number;
	goal_difference: number;
	metric_value: number;
	unit: string;
}

export interface AnalyticsResponse {
	metric: string;
	formula: string;
	venue_filter: string;
	series: AnalyticsSeriesItem[];
	computed_at: string;
	disclaimer: string;
}

export interface Insight {
	id: string;
	user_id?: string | null;
	author_name: string;
	author_club_id: string;
	title: string;
	description?: string | null;
	metric: string;
	team_ids: string[];
	venue: string;
	competition_id?: string | null;
	chart_type: string;
	snapshot: AnalyticsResponse;
	is_public: boolean;
	created_at: string;
}

export interface InsightCreatePayload {
	title: string;
	description?: string;
	metric: string;
	team_ids: string[];
	venue: string;
	competition_id?: string;
	chart_type?: string;
	author_name?: string;
	author_club_id?: string;
	snapshot?: AnalyticsResponse;
}

export interface Post {
	id: string;
	author_id?: string | null;
	author_name: string;
	author_club_id: string;
	club_id?: string | null;
	content: string;
	insight_id?: string | null;
	insight?: Insight | null;
	created_at: string;
	reactions_count: number;
	comments_count: number;
	user_reacted: boolean;
}

export interface PostComment {
	id: string;
	post_id: string;
	author_id?: string | null;
	author_name: string;
	author_club_id: string;
	content: string;
	created_at: string;
}

export interface PostCreatePayload {
	content: string;
	club_id?: string | null;
	insight_id?: string | null;
	author_name?: string;
	author_club_id?: string;
}

export interface DirectMessage {
	id: string;
	conversation_id: string;
	sender_id: string;
	sender_name: string;
	sender_club_id: string;
	content: string;
	created_at: string;
}

export interface Conversation {
	id: string;
	created_at: string;
	updated_at: string;
	members: string[];
	last_message?: DirectMessage | null;
}

export interface Player {
	id: string;
	club_id: string;
	name: string;
	short_name: string;
	position: string;
	jersey_number: number;
	nationality: string;
	appearances: number;
	goals: number;
	assists: number;
	clean_sheets: number;
	minutes_played: number;
	yellow_cards: number;
	red_cards: number;
	photo_url?: string | null;
	goals_per_game: number;
	assists_per_game: number;
	goal_contributions: number;
}

export interface PlayerComparisonItem {
	player: Player;
	goals_per_90: number;
	assists_per_90: number;
	minutes_per_contribution: number;
	discipline_score: number;
}

export interface PlayerComparison {
	player1: PlayerComparisonItem;
	player2: PlayerComparisonItem;
	comparison_summary: string;
}

export interface Prediction {
	id: string;
	user_id: string;
	user_name: string;
	user_club_id: string;
	match_id: string;
	predicted_home_score: number;
	predicted_away_score: number;
	points_awarded?: number | null;
	created_at: string;
}

export interface UpcomingMatchPrediction {
	match: Match;
	user_prediction?: Prediction | null;
	can_predict: boolean;
	total_predictions_count: number;
}

export interface LeaderboardEntry {
	rank: number;
	user_id: string;
	user_name: string;
	user_club_id: string;
	total_points: number;
	predictions_count: number;
	exact_scores: number;
	correct_outcomes: number;
	accuracy_rate: number;
}

export interface Notification {
	id: string;
	user_id: string;
	type: string;
	title: string;
	message: string;
	link: string;
	is_read: boolean;
	created_at: string;
}

export interface SupporterStats {
	prediction_points: number;
	prediction_rank: number;
	total_predictions: number;
	exact_scores: number;
	insights_published: number;
	posts_count: number;
	cheers_received: number;
}

export interface SupporterProfile {
	user_id: string;
	username: string;
	display_name: string;
	favorite_club_id: string;
	bio?: string | null;
	joined_at: string;
	stats: SupporterStats;
	featured_insights: Insight[];
	recent_posts: Post[];
}

export interface ShotEvent {
	id: string;
	minute: number;
	second: number;
	team_id: string;
	team_name: string;
	player_name: string;
	x: number;
	y: number;
	outcome: string;
	xg: number;
	body_part: string;
	shot_type: string;
}

export interface PassNode {
	player_name: string;
	position: string;
	jersey_number: number;
	x: number;
	y: number;
	passes_completed: number;
}

export interface PassLink {
	source: string;
	target: string;
	pass_count: number;
}

export interface HistoricalMatchSummary {
	id: string;
	title: string;
	competition: string;
	season: string;
	match_date: string;
	venue: string;
	home_team_id: string;
	home_team_name: string;
	home_score: number;
	away_team_id: string;
	away_team_name: string;
	away_score: number;
	data_provider: string;
	license_notice: string;
}

export interface HistoricalMatchDetail extends HistoricalMatchSummary {
	shots: ShotEvent[];
	pass_nodes: PassNode[];
	pass_links: PassLink[];
	total_shots_home: number;
	total_shots_away: number;
	total_xg_home: number;
	total_xg_away: number;
}

export interface TopicTag {
	tag: string;
	count: number;
	club: string;
}


