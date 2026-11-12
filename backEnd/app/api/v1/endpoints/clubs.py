from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.clubs import ClubResponse

router = APIRouter()

# Arsenal FC is the sole foundation club; comparison opponents remain available for Data Lab matchups.
INITIAL_CLUBS: List[dict] = [
    {
        "id": "arsenal",
        "slug": "arsenal",
        "name": "Arsenal FC",
        "short_name": "Arsenal",
        "primary_color": "#EF0107",
        "secondary_color": "#FFFFFF",
        "accent_color": "#9C824A",
        "league": "Premier League",
        "country": "England",
        "crest_url": "https://crests.football-data.org/57.png",
        "is_foundation": True,
        "is_active": True,
    },
    {
        "id": "real-madrid",
        "slug": "real-madrid",
        "name": "Real Madrid CF",
        "short_name": "Real Madrid",
        "primary_color": "#FFFFFF",
        "secondary_color": "#00529F",
        "accent_color": "#EEB028",
        "league": "La Liga",
        "country": "Spain",
        "crest_url": "https://crests.football-data.org/86.png",
        "is_foundation": False,
        "is_active": True,
    },
    {
        "id": "barcelona",
        "slug": "barcelona",
        "name": "FC Barcelona",
        "short_name": "Barcelona",
        "primary_color": "#A50044",
        "secondary_color": "#004D98",
        "accent_color": "#EDBB00",
        "league": "La Liga",
        "country": "Spain",
        "crest_url": "https://crests.football-data.org/81.png",
        "is_foundation": False,
        "is_active": True,
    },
    {
        "id": "milan",
        "slug": "milan",
        "name": "AC Milan",
        "short_name": "AC Milan",
        "primary_color": "#FB090B",
        "secondary_color": "#000000",
        "accent_color": "#C0C0C0",
        "league": "Serie A",
        "country": "Italy",
        "crest_url": "https://crests.football-data.org/98.png",
        "is_foundation": False,
        "is_active": True,
    },
]


@router.get("", response_model=List[ClubResponse])
async def list_clubs():
    """Retrieve Arsenal FC (foundation club) and supported Data Lab comparison opponents."""
    return INITIAL_CLUBS


@router.get("/{club_slug}", response_model=ClubResponse)
async def get_club(club_slug: str):
    """Retrieve a single club by its slug."""
    for club in INITIAL_CLUBS:
        if club["slug"] == club_slug:
            return club
    raise HTTPException(status_code=404, detail="Club not found")
