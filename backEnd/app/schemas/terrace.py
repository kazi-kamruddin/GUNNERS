from pydantic import BaseModel, Field
from typing import Optional, List
import datetime
from app.schemas.insight import InsightResponse
from app.schemas.tactics import TacticalBoardResponse

class PostCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    club_id: Optional[str] = None  # None or specific club id
    insight_id: Optional[str] = None
    tactical_board_id: Optional[str] = None
    author_name: str = Field("Supporter", max_length=100)
    author_club_id: str = Field("arsenal", max_length=50)

class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    author_name: str = Field("Supporter", max_length=100)
    author_club_id: str = Field("arsenal", max_length=50)

class ReactionToggleRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    reaction_type: str = Field("cheer", max_length=20)

class CommentResponse(BaseModel):
    id: str
    post_id: str
    author_id: Optional[str] = None
    author_name: str
    author_club_id: str
    content: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class PostResponse(BaseModel):
    id: str
    author_id: Optional[str] = None
    author_name: str
    author_club_id: str
    club_id: Optional[str] = None
    content: str
    insight_id: Optional[str] = None
    insight: Optional[InsightResponse] = None
    tactical_board_id: Optional[str] = None
    tactical_board: Optional[TacticalBoardResponse] = None
    created_at: datetime.datetime
    reactions_count: int = 0
    comments_count: int = 0
    user_reacted: bool = False

    model_config = {"from_attributes": True}
