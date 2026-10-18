from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
from app.schemas.analytics import AnalyticsResponse

class InsightCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    metric: str = Field(..., pattern="^(win_rate|goals_per_match|points_per_game|goal_difference|clean_sheet_rate|loss_rate)$")
    team_ids: List[str] = Field(..., min_length=1, max_length=2)
    venue: str = Field("all", pattern="^(all|home|away)$")
    competition_id: Optional[str] = None
    chart_type: str = Field("bar", pattern="^(bar|comparison|distribution)$")
    author_name: str = Field("Supporter", max_length=100)
    author_club_id: str = Field("arsenal", max_length=50)
    snapshot: Optional[AnalyticsResponse] = None

class InsightResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    author_name: str
    author_club_id: str
    title: str
    description: Optional[str] = None
    metric: str
    team_ids: List[str]
    venue: str
    competition_id: Optional[str] = None
    chart_type: str
    snapshot: AnalyticsResponse
    is_public: bool = True
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
