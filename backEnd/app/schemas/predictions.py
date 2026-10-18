from pydantic import BaseModel, Field
from typing import Optional, List
import datetime
from app.schemas.analytics import MatchResponse

class PredictionCreateRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    user_name: str = Field("Supporter", max_length=100)
    user_club_id: str = Field("arsenal", max_length=50)
    match_id: str = Field(..., max_length=50)
    predicted_home_score: int = Field(..., ge=0, le=20)
    predicted_away_score: int = Field(..., ge=0, le=20)

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_club_id: str
    match_id: str
    predicted_home_score: int
    predicted_away_score: int
    points_awarded: Optional[int] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class UpcomingMatchPredictionItem(BaseModel):
    match: MatchResponse
    user_prediction: Optional[PredictionResponse] = None
    can_predict: bool = True
    total_predictions_count: int = 0

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    user_name: str
    user_club_id: str
    total_points: int
    predictions_count: int
    exact_scores: int
    correct_outcomes: int
    accuracy_rate: float
