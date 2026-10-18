from pydantic import BaseModel
from typing import List, Optional

class ShotEvent(BaseModel):
    id: str
    minute: int
    second: int
    team_id: str
    team_name: str
    player_name: str
    x: float  # 0 to 100 on attacking pitch length
    y: float  # 0 to 100 on pitch width
    outcome: str  # Goal, Saved, Blocked, Miss, Off Post
    xg: float
    body_part: str
    shot_type: str

class PassNode(BaseModel):
    player_name: str
    position: str
    jersey_number: int
    x: float  # average x position
    y: float  # average y position
    passes_completed: int

class PassLink(BaseModel):
    source: str  # player_name
    target: str  # player_name
    pass_count: int

class HistoricalMatchSummary(BaseModel):
    id: str
    title: str
    competition: str
    season: str
    match_date: str
    venue: str
    home_team_id: str
    home_team_name: str
    home_score: int
    away_team_id: str
    away_team_name: str
    away_score: int
    data_provider: str = "StatsBomb Open Data"
    license_notice: str = "Event data provided by StatsBomb under open-data terms."

class HistoricalMatchDetail(HistoricalMatchSummary):
    shots: List[ShotEvent] = []
    pass_nodes: List[PassNode] = []
    pass_links: List[PassLink] = []
    total_shots_home: int = 0
    total_shots_away: int = 0
    total_xg_home: float = 0.0
    total_xg_away: float = 0.0
