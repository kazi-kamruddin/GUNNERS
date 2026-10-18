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
}

export interface Match {
	id: string;
	competition_id: string;
	season_id: string;
	home_team_id: string;
	away_team_id: string;
	matchday?: number;
	utc_date: string;
	status: string;
	venue?: string;
	home_score?: number;
	away_score?: number;
	winner?: string;
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
