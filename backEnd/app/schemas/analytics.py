from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

class MatchFilterParams(BaseModel):
    club_id: Optional[str] = None
    competition_id: Optional[str] = None
    season_id: Optional[str] = None
    status: Optional[str] = None
    venue: Optional[str] = Field(None, pattern="^(all|home|away)$")
    limit: int = Field(50, ge=1, le=100)

class MatchResponse(BaseModel):
    id: str
    competition_id: Optional[str] = None
    competition_name: Optional[str] = None
    season_id: str
    home_team_id: str
    home_team_name: str = "Home Team"
    home_team_crest: Optional[str] = None
    away_team_id: str
    away_team_name: str = "Away Team"
    away_team_crest: Optional[str] = None
    matchday: Optional[int] = None
    utc_date: datetime.datetime
    status: str
    venue: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[str] = None
    source: Optional[str] = "football-data.org"
    last_updated_at: Optional[datetime.datetime] = None

    model_config = {"from_attributes": True}

class MatchSummaryResponse(BaseModel):
    club_id: str
    club_name: str
    next_fixture: Optional[MatchResponse] = None
    last_result: Optional[MatchResponse] = None
    recent_form: List[str] = []
    total_completed: int = 0
    total_scheduled: int = 0

class SyncStatusResponse(BaseModel):
    latest_sync: Optional[datetime.datetime] = None
    status: str
    source: str
    matches_synced: int
    error_message: Optional[str] = None

class AnalyticsQueryRequest(BaseModel):
    metric: str = Field(..., pattern="^(win_rate|goals_per_match|points_per_game|goal_difference)$")
    team_ids: List[str] = Field(..., min_length=1, max_length=2)
    competition_id: Optional[str] = None
    season_id: Optional[str] = None
    venue: str = Field("all", pattern="^(all|home|away)$")

class AnalyticsSeriesItem(BaseModel):
    team_id: str
    team_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    metric_value: float
    unit: str

class AnalyticsResponse(BaseModel):
    metric: str
    formula: str
    venue_filter: str
    series: List[AnalyticsSeriesItem]
    computed_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    disclaimer: str = "Calculated strictly across eligible completed matches."
