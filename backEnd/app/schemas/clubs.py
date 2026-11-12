from typing import Optional
from pydantic import BaseModel


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
    crest_url: Optional[str] = None
    is_foundation: bool = False
    is_active: bool = True


class ClubResponse(ClubBase):
    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    environment: str
