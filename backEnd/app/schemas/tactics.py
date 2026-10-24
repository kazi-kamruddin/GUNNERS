from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class PlayerToken(BaseModel):
    id: str
    name: str = Field(..., max_length=100)
    number: int = Field(..., ge=1, le=99)
    role: str = Field(..., max_length=20)
    x: float = Field(..., ge=0.0, le=100.0)
    y: float = Field(..., ge=0.0, le=100.0)

class AnnotationItem(BaseModel):
    id: str
    type: str = Field("run", max_length=20)  # run, pass, press
    from_x: float = Field(..., ge=0.0, le=100.0)
    from_y: float = Field(..., ge=0.0, le=100.0)
    to_x: float = Field(..., ge=0.0, le=100.0)
    to_y: float = Field(..., ge=0.0, le=100.0)
    label: Optional[str] = None

class FormationPreset(BaseModel):
    id: str
    name: str
    description: str
    players: List[PlayerToken]

class TacticalBoardCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    formation: str = Field("4-3-3", max_length=20)
    lineup: List[PlayerToken]
    annotations: Optional[List[AnnotationItem]] = []
    tactical_notes: Optional[str] = Field(None, max_length=3000)
    author_name: str = Field("Supporter", max_length=100)
    author_club_id: str = Field("arsenal", max_length=50)
    user_id: Optional[str] = None
    is_public: bool = True

class TacticalBoardResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    author_name: str
    author_club_id: str
    title: str
    formation: str
    lineup: List[PlayerToken]
    annotations: List[AnnotationItem] = []
    tactical_notes: Optional[str] = None
    is_public: bool = True
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
