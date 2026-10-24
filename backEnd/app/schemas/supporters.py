from pydantic import BaseModel
from typing import Optional, List
import datetime
from app.schemas.insight import InsightResponse
from app.schemas.terrace import PostResponse

class SupporterStats(BaseModel):
    prediction_points: int = 0
    prediction_rank: int = 1
    total_predictions: int = 0
    exact_scores: int = 0
    insights_published: int = 0
    posts_count: int = 0
    cheers_received: int = 0

class SupporterProfileResponse(BaseModel):
    user_id: str
    username: str
    display_name: str
    favorite_club_id: str
    bio: Optional[str] = None
    joined_at: datetime.datetime
    stats: SupporterStats
    featured_insights: List[InsightResponse] = []
    recent_posts: List[PostResponse] = []
