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
