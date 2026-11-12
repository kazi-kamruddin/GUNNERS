from pydantic import BaseModel
from typing import Optional


class PlayerResponse(BaseModel):
    id: str
    club_id: str
    name: str
    short_name: str
    position: str
    jersey_number: int
    nationality: str
    appearances: int
    goals: int
    assists: int
    clean_sheets: int
    minutes_played: int
    yellow_cards: int
    red_cards: int
    photo_url: Optional[str] = None
    portrait_url: Optional[str] = None
    action_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    height: Optional[str] = None
    joined_date: Optional[str] = None
    goals_per_game: float = 0.0
    assists_per_game: float = 0.0
    goal_contributions: int = 0

    model_config = {"from_attributes": True}


class PlayerComparisonItem(BaseModel):
    player: PlayerResponse
    goals_per_90: float
    assists_per_90: float
    minutes_per_contribution: float
    discipline_score: float


class PlayerComparisonResponse(BaseModel):
    player1: PlayerComparisonItem
    player2: PlayerComparisonItem
    comparison_summary: str
