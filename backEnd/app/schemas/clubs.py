from pydantic import BaseModel
from typing import List, Optional

class ClubBase(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    league: str
    country: str

class ClubResponse(ClubBase):
    pass

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    environment: str
