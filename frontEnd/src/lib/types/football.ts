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

