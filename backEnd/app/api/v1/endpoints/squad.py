from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.core.database import get_db
from app.models.squad import Player
from app.schemas.squad import (
    PlayerResponse,
    PlayerComparisonResponse,
    PlayerComparisonItem
)

router = APIRouter()

# Curated Arsenal FC 2024/25 First Team Squad
DEFAULT_PLAYERS: List[dict] = [
    # Goalkeepers
    {
        "id": "ply_raya",
        "club_id": "arsenal",
        "name": "David Raya",
        "short_name": "D. Raya",
        "position": "Goalkeeper",
        "jersey_number": 22,
        "nationality": "Spain",
        "appearances": 22,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 10,
        "minutes_played": 1980,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_neto",
        "club_id": "arsenal",
        "name": "Neto",
        "short_name": "Neto",
        "position": "Goalkeeper",
        "jersey_number": 32,
        "nationality": "Brazil",
        "appearances": 3,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 1,
        "minutes_played": 270,
        "yellow_cards": 0,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_setford",
        "club_id": "arsenal",
        "name": "Tommy Setford",
        "short_name": "T. Setford",
        "position": "Goalkeeper",
        "jersey_number": 36,
        "nationality": "England",
        "appearances": 1,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 1,
        "minutes_played": 90,
        "yellow_cards": 0,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    # Defenders
    {
        "id": "ply_saliba",
        "club_id": "arsenal",
        "name": "William Saliba",
        "short_name": "W. Saliba",
        "position": "Defender",
        "jersey_number": 2,
        "nationality": "France",
        "appearances": 21,
        "goals": 1,
        "assists": 0,
        "clean_sheets": 9,
        "minutes_played": 1845,
        "yellow_cards": 2,
        "red_cards": 1,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_gabriel",
        "club_id": "arsenal",
        "name": "Gabriel Magalhães",
        "short_name": "Gabriel",
        "position": "Defender",
        "jersey_number": 6,
        "nationality": "Brazil",
        "appearances": 22,
        "goals": 3,
        "assists": 0,
        "clean_sheets": 9,
        "minutes_played": 1910,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_white",
        "club_id": "arsenal",
        "name": "Ben White",
        "short_name": "B. White",
        "position": "Defender",
        "jersey_number": 4,
        "nationality": "England",
        "appearances": 16,
        "goals": 1,
        "assists": 2,
        "clean_sheets": 6,
        "minutes_played": 1280,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_timber",
        "club_id": "arsenal",
        "name": "Jurriën Timber",
        "short_name": "J. Timber",
        "position": "Defender",
        "jersey_number": 12,
        "nationality": "Netherlands",
        "appearances": 20,
        "goals": 1,
        "assists": 2,
        "clean_sheets": 8,
        "minutes_played": 1530,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_calafiori",
        "club_id": "arsenal",
        "name": "Riccardo Calafiori",
        "short_name": "R. Calafiori",
        "position": "Defender",
        "jersey_number": 33,
        "nationality": "Italy",
        "appearances": 15,
        "goals": 1,
        "assists": 1,
        "clean_sheets": 5,
        "minutes_played": 980,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_zinchenko",
        "club_id": "arsenal",
        "name": "Oleksandr Zinchenko",
        "short_name": "O. Zinchenko",
        "position": "Defender",
        "jersey_number": 17,
        "nationality": "Ukraine",
        "appearances": 11,
        "goals": 0,
        "assists": 1,
        "clean_sheets": 3,
        "minutes_played": 490,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_tomiyasu",
        "club_id": "arsenal",
        "name": "Takehiro Tomiyasu",
        "short_name": "T. Tomiyasu",
        "position": "Defender",
        "jersey_number": 18,
        "nationality": "Japan",
        "appearances": 6,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 2,
        "minutes_played": 210,
        "yellow_cards": 0,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_kiwior",
        "club_id": "arsenal",
        "name": "Jakub Kiwior",
        "short_name": "J. Kiwior",
        "position": "Defender",
        "jersey_number": 15,
        "nationality": "Poland",
        "appearances": 12,
        "goals": 0,
        "assists": 1,
        "clean_sheets": 4,
        "minutes_played": 640,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    # Midfielders
    {
        "id": "ply_rice",
        "club_id": "arsenal",
        "name": "Declan Rice",
        "short_name": "D. Rice",
        "position": "Midfielder",
        "jersey_number": 41,
        "nationality": "England",
        "appearances": 23,
        "goals": 3,
        "assists": 4,
        "clean_sheets": 0,
        "minutes_played": 1950,
        "yellow_cards": 3,
        "red_cards": 1,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_odegaard",
        "club_id": "arsenal",
        "name": "Martin Ødegaard",
        "short_name": "M. Ødegaard",
        "position": "Midfielder",
        "jersey_number": 8,
        "nationality": "Norway",
        "appearances": 18,
        "goals": 5,
        "assists": 7,
        "clean_sheets": 0,
        "minutes_played": 1510,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_merino",
        "club_id": "arsenal",
        "name": "Mikel Merino",
        "short_name": "M. Merino",
        "position": "Midfielder",
        "jersey_number": 23,
        "nationality": "Spain",
        "appearances": 17,
        "goals": 2,
        "assists": 1,
        "clean_sheets": 0,
        "minutes_played": 920,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_partey",
        "club_id": "arsenal",
        "name": "Thomas Partey",
        "short_name": "T. Partey",
        "position": "Midfielder",
        "jersey_number": 5,
        "nationality": "Ghana",
        "appearances": 21,
        "goals": 2,
        "assists": 1,
        "clean_sheets": 0,
        "minutes_played": 1620,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_jorginho",
        "club_id": "arsenal",
        "name": "Jorginho",
        "short_name": "Jorginho",
        "position": "Midfielder",
        "jersey_number": 20,
        "nationality": "Italy",
        "appearances": 14,
        "goals": 0,
        "assists": 1,
        "clean_sheets": 0,
        "minutes_played": 740,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_nwaneri",
        "club_id": "arsenal",
        "name": "Ethan Nwaneri",
        "short_name": "E. Nwaneri",
        "position": "Midfielder",
        "jersey_number": 53,
        "nationality": "England",
        "appearances": 12,
        "goals": 4,
        "assists": 1,
        "clean_sheets": 0,
        "minutes_played": 460,
        "yellow_cards": 0,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    # Attackers / Forwards
    {
        "id": "ply_saka",
        "club_id": "arsenal",
        "name": "Bukayo Saka",
        "short_name": "B. Saka",
        "position": "Attacker",
        "jersey_number": 7,
        "nationality": "England",
        "appearances": 22,
        "goals": 9,
        "assists": 11,
        "clean_sheets": 0,
        "minutes_played": 1820,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_havertz",
        "club_id": "arsenal",
        "name": "Kai Havertz",
        "short_name": "K. Havertz",
        "position": "Attacker",
        "jersey_number": 29,
        "nationality": "Germany",
        "appearances": 23,
        "goals": 11,
        "assists": 4,
        "clean_sheets": 0,
        "minutes_played": 1880,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_martinelli",
        "club_id": "arsenal",
        "name": "Gabriel Martinelli",
        "short_name": "G. Martinelli",
        "position": "Attacker",
        "jersey_number": 11,
        "nationality": "Brazil",
        "appearances": 22,
        "goals": 6,
        "assists": 5,
        "clean_sheets": 0,
        "minutes_played": 1580,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_trossard",
        "club_id": "arsenal",
        "name": "Leandro Trossard",
        "short_name": "L. Trossard",
        "position": "Attacker",
        "jersey_number": 19,
        "nationality": "Belgium",
        "appearances": 21,
        "goals": 6,
        "assists": 3,
        "clean_sheets": 0,
        "minutes_played": 1210,
        "yellow_cards": 2,
        "red_cards": 1,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_jesus",
        "club_id": "arsenal",
        "name": "Gabriel Jesus",
        "short_name": "G. Jesus",
        "position": "Attacker",
        "jersey_number": 9,
        "nationality": "Brazil",
        "appearances": 16,
        "goals": 3,
        "assists": 2,
        "clean_sheets": 0,
        "minutes_played": 790,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    },
    {
        "id": "ply_sterling",
        "club_id": "arsenal",
        "name": "Raheem Sterling",
        "short_name": "R. Sterling",
        "position": "Attacker",
        "jersey_number": 30,
        "nationality": "England",
        "appearances": 14,
        "goals": 1,
        "assists": 2,
        "clean_sheets": 0,
        "minutes_played": 580,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://crests.football-data.org/57.png"
    }
]

def _player_model_to_dict(p: Player) -> dict:
    return {
        "id": p.id,
        "club_id": p.club_id,
        "name": p.name,
        "short_name": p.short_name,
        "position": p.position,
        "jersey_number": p.jersey_number,
        "nationality": p.nationality,
        "appearances": p.appearances,
        "goals": p.goals,
        "assists": p.assists,
        "clean_sheets": p.clean_sheets,
        "minutes_played": p.minutes_played,
        "yellow_cards": p.yellow_cards,
        "red_cards": p.red_cards,
        "photo_url": p.photo_url,
        "portrait_url": p.portrait_url,
        "action_url": p.action_url,
        "bio": p.bio,
        "date_of_birth": p.date_of_birth,
        "height": p.height,
        "joined_date": p.joined_date,
    }


def format_player_response(p: dict) -> PlayerResponse:
    apps = max(p.get("appearances", 1), 1)
    goals = p.get("goals", 0)
    assists = p.get("assists", 0)
    return PlayerResponse(
        id=p["id"],
        club_id=p["club_id"],
        name=p["name"],
        short_name=p["short_name"],
        position=p["position"],
        jersey_number=p["jersey_number"],
        nationality=p["nationality"],
        appearances=p.get("appearances", 0),
        goals=goals,
        assists=assists,
        clean_sheets=p.get("clean_sheets", 0),
        minutes_played=p.get("minutes_played", 0),
        yellow_cards=p.get("yellow_cards", 0),
        red_cards=p.get("red_cards", 0),
        photo_url=p.get("photo_url"),
        portrait_url=p.get("portrait_url"),
        action_url=p.get("action_url"),
        bio=p.get("bio"),
        date_of_birth=p.get("date_of_birth"),
        height=p.get("height"),
        joined_date=p.get("joined_date"),
        goals_per_game=round(goals / apps, 2),
        assists_per_game=round(assists / apps, 2),
        goal_contributions=goals + assists
    )

def build_comparison_item(p: PlayerResponse) -> PlayerComparisonItem:
    minutes = max(p.minutes_played, 90)
    contributions = max(p.goal_contributions, 1)
    return PlayerComparisonItem(
        player=p,
        goals_per_90=round((p.goals / minutes) * 90, 2),
        assists_per_90=round((p.assists / minutes) * 90, 2),
        minutes_per_contribution=round(minutes / contributions, 1),
        discipline_score=round(10.0 - (p.yellow_cards * 0.5 + p.red_cards * 2.0), 1)
    )

@router.get("", response_model=List[PlayerResponse])
async def list_squad(
    club_id: Optional[str] = Query(None, description="Filter squad by club"),
    position: Optional[str] = Query(None, description="Filter by position (Goalkeeper, Defender, Midfielder, Attacker)"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve club squad list with full player profiles and statistics (DB-first)."""
    total_in_db = (await db.execute(select(func.count(Player.id)))).scalar() or 0
    if total_in_db > 0:
        stmt = select(Player)
        if club_id:
            stmt = stmt.where(Player.club_id == club_id)
        if position:
            stmt = stmt.where(func.lower(Player.position) == position.lower())
        stmt = stmt.order_by(Player.jersey_number.asc())
        db_players = (await db.execute(stmt)).scalars().all()
        return [format_player_response(_player_model_to_dict(p)) for p in db_players]

    # Cold-start baseline fallback when players table is empty
    players = DEFAULT_PLAYERS
    if club_id:
        players = [p for p in players if p["club_id"] == club_id]
    if position:
        players = [p for p in players if p["position"].lower() == position.lower()]

    return [format_player_response(p) for p in players]


@router.get("/compare", response_model=PlayerComparisonResponse)
async def compare_players(
    player1_id: str = Query(..., description="First player ID"),
    player2_id: str = Query(..., description="Second player ID"),
    db: AsyncSession = Depends(get_db)
):
    """Compare two players head-to-head across key performance metrics (DB-first)."""
    db_p1 = (await db.execute(select(Player).where(Player.id == player1_id))).scalar_one_or_none()
    db_p2 = (await db.execute(select(Player).where(Player.id == player2_id))).scalar_one_or_none()

    p1_dict = _player_model_to_dict(db_p1) if db_p1 else None
    p2_dict = _player_model_to_dict(db_p2) if db_p2 else None

    if not p1_dict or not p2_dict:
        total_in_db = (await db.execute(select(func.count(Player.id)))).scalar() or 0
        if total_in_db == 0:
            if not p1_dict:
                p1_dict = next((p for p in DEFAULT_PLAYERS if p["id"] == player1_id), None)
            if not p2_dict:
                p2_dict = next((p for p in DEFAULT_PLAYERS if p["id"] == player2_id), None)

    if not p1_dict or not p2_dict:
        raise HTTPException(status_code=404, detail="One or both players not found")

    p1_resp = format_player_response(p1_dict)
    p2_resp = format_player_response(p2_dict)

    item1 = build_comparison_item(p1_resp)
    item2 = build_comparison_item(p2_resp)

    if item1.player.goal_contributions > item2.player.goal_contributions:
        leader = item1.player.name
        summary = f"{leader} leads in total direct goal contributions ({item1.player.goal_contributions} vs {item2.player.goal_contributions})."
    elif item2.player.goal_contributions > item1.player.goal_contributions:
        leader = item2.player.name
        summary = f"{leader} leads in total direct goal contributions ({item2.player.goal_contributions} vs {item1.player.goal_contributions})."
    else:
        summary = f"Both players are level with {item1.player.goal_contributions} direct goal contributions."

    return PlayerComparisonResponse(
        player1=item1,
        player2=item2,
        comparison_summary=summary
    )


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single player profile details (DB-first)."""
    db_p = (await db.execute(select(Player).where(Player.id == player_id))).scalar_one_or_none()
    if db_p:
        return format_player_response(_player_model_to_dict(db_p))

    total_in_db = (await db.execute(select(func.count(Player.id)))).scalar() or 0
    if total_in_db == 0:
        p_dict = next((p for p in DEFAULT_PLAYERS if p["id"] == player_id), None)
        if p_dict:
            return format_player_response(p_dict)

    raise HTTPException(status_code=404, detail="Player not found")
