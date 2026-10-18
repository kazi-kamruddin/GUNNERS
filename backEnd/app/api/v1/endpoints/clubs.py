from fastapi import APIRouter
from typing import List
from app.schemas.clubs import ClubResponse

router = APIRouter()

# The four foundational clubs as per Gunners_PROJECT_DIRECTION.md
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
    },
]

@router.get("", response_model=List[ClubResponse])
async def list_clubs():
    """Retrieve all supported clubs."""
    return INITIAL_CLUBS

@router.get("/{club_slug}", response_model=ClubResponse)
async def get_club(club_slug: str):
    """Retrieve a single club by its slug."""
    for club in INITIAL_CLUBS:
        if club["slug"] == club_slug:
            return club
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Club not found")
