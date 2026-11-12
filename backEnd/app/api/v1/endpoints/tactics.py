from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from typing import List, Optional
import uuid
import datetime

from app.core.database import get_db
from app.core.security import CurrentUserDep, OptionalUserDep
from app.models.tactics import TacticalBoard
from app.schemas.tactics import (
    TacticalBoardCreate,
    TacticalBoardResponse,
    FormationPreset,
    PlayerToken,
)

router = APIRouter()

PRESETS: List[FormationPreset] = [
    FormationPreset(
        id="4-3-3",
        name="4-3-3 Attacking",
        description="High press with aggressive wingers and a single holding midfielder.",
        players=[
            PlayerToken(id="p1", name="Raya", number=1, role="GK", x=5.0, y=50.0),
            PlayerToken(id="p2", name="Zinchenko", number=35, role="LB", x=24.0, y=14.0),
            PlayerToken(id="p3", name="Gabriel", number=6, role="CB", x=20.0, y=36.0),
            PlayerToken(id="p4", name="Saliba", number=2, role="CB", x=20.0, y=64.0),
            PlayerToken(id="p5", name="White", number=4, role="RB", x=24.0, y=86.0),
            PlayerToken(id="p6", name="Rice", number=41, role="DM", x=38.0, y=50.0),
            PlayerToken(id="p7", name="Merino", number=23, role="CM", x=54.0, y=30.0),
            PlayerToken(id="p8", name="Ødegaard", number=8, role="CM", x=54.0, y=70.0),
            PlayerToken(id="p9", name="Martinelli", number=11, role="LW", x=76.0, y=16.0),
            PlayerToken(id="p10", name="Havertz", number=29, role="ST", x=82.0, y=50.0),
            PlayerToken(id="p11", name="Saka", number=7, role="RW", x=76.0, y=84.0),
        ],
    ),
    FormationPreset(
        id="4-2-3-1",
        name="4-2-3-1 Double Pivot",
        description="Controlled midfield with Rice-Partey double pivot and Ødegaard orchestrating in the hole.",
        players=[
            PlayerToken(id="p1", name="Raya", number=22, role="GK", x=5.0, y=50.0),
            PlayerToken(id="p2", name="Calafiori", number=33, role="LB", x=24.0, y=14.0),
            PlayerToken(id="p3", name="Gabriel", number=6, role="CB", x=20.0, y=36.0),
            PlayerToken(id="p4", name="Saliba", number=2, role="CB", x=20.0, y=64.0),
            PlayerToken(id="p5", name="Timber", number=12, role="RB", x=24.0, y=86.0),
            PlayerToken(id="p6", name="Rice", number=41, role="DM", x=38.0, y=35.0),
            PlayerToken(id="p7", name="Partey", number=5, role="DM", x=38.0, y=65.0),
            PlayerToken(id="p8", name="Ødegaard", number=8, role="AM", x=58.0, y=50.0),
            PlayerToken(id="p9", name="Martinelli", number=11, role="LW", x=72.0, y=18.0),
            PlayerToken(id="p10", name="Saka", number=7, role="RW", x=72.0, y=82.0),
            PlayerToken(id="p11", name="Havertz", number=29, role="ST", x=84.0, y=50.0),
        ],
    ),
    FormationPreset(
        id="3-4-2-1",
        name="3-4-2-1 Box Midfield",
        description="Asymmetrical 3-back build-up with dual attacking #10s and wide wing-backs.",
        players=[
            PlayerToken(id="p1", name="Goalkeeper", number=1, role="GK", x=5.0, y=50.0),
            PlayerToken(id="p2", name="Left CB", number=6, role="CB", x=22.0, y=25.0),
            PlayerToken(id="p3", name="Central CB", number=2, role="CB", x=18.0, y=50.0),
            PlayerToken(id="p4", name="Right CB", number=12, role="CB", x=22.0, y=75.0),
            PlayerToken(id="p5", name="Left Wingback", number=3, role="LWB", x=45.0, y=10.0),
            PlayerToken(id="p6", name="Pivot 1", number=41, role="CM", x=42.0, y=38.0),
            PlayerToken(id="p7", name="Pivot 2", number=8, role="CM", x=42.0, y=62.0),
            PlayerToken(id="p8", name="Right Wingback", number=4, role="RWB", x=45.0, y=90.0),
            PlayerToken(id="p9", name="Inside Left #10", number=19, role="AM", x=68.0, y=32.0),
            PlayerToken(id="p10", name="Inside Right #10", number=10, role="AM", x=68.0, y=68.0),
            PlayerToken(id="p11", name="Striker", number=9, role="ST", x=84.0, y=50.0),
        ],
    ),
    FormationPreset(
        id="4-4-2",
        name="4-4-2 Traditional",
        description="Compact defensive banks of four with direct flank play and dual strikers.",
        players=[
            PlayerToken(id="p1", name="Goalkeeper", number=1, role="GK", x=5.0, y=50.0),
            PlayerToken(id="p2", name="Left Back", number=3, role="LB", x=24.0, y=14.0),
            PlayerToken(id="p3", name="Left CB", number=6, role="CB", x=20.0, y=36.0),
            PlayerToken(id="p4", name="Right CB", number=2, role="CB", x=20.0, y=64.0),
            PlayerToken(id="p5", name="Right Back", number=4, role="RB", x=24.0, y=86.0),
            PlayerToken(id="p6", name="Left Mid", number=11, role="LM", x=52.0, y=15.0),
            PlayerToken(id="p7", name="Center Mid", number=41, role="CM", x=46.0, y=38.0),
            PlayerToken(id="p8", name="Center Mid", number=8, role="CM", x=46.0, y=62.0),
            PlayerToken(id="p9", name="Right Mid", number=7, role="RM", x=52.0, y=85.0),
            PlayerToken(id="p10", name="Left Striker", number=14, role="ST", x=80.0, y=38.0),
            PlayerToken(id="p11", name="Right Striker", number=9, role="ST", x=80.0, y=62.0),
        ],
    ),
    FormationPreset(
        id="3-5-2",
        name="3-5-2 Wing Play",
        description="Midfield overload with energetic wing-backs and tandem front two.",
        players=[
            PlayerToken(id="p1", name="Goalkeeper", number=1, role="GK", x=5.0, y=50.0),
            PlayerToken(id="p2", name="Left CB", number=6, role="CB", x=22.0, y=25.0),
            PlayerToken(id="p3", name="Sweeper CB", number=2, role="CB", x=18.0, y=50.0),
            PlayerToken(id="p4", name="Right CB", number=12, role="CB", x=22.0, y=75.0),
            PlayerToken(id="p5", name="Left Wingback", number=3, role="LWB", x=48.0, y=10.0),
            PlayerToken(id="p6", name="Holding Mid", number=41, role="DM", x=36.0, y=50.0),
            PlayerToken(id="p7", name="Left Interior", number=23, role="CM", x=55.0, y=32.0),
            PlayerToken(id="p8", name="Right Interior", number=8, role="CM", x=55.0, y=68.0),
            PlayerToken(id="p9", name="Right Wingback", number=4, role="RWB", x=48.0, y=90.0),
            PlayerToken(id="p10", name="Left Forward", number=29, role="ST", x=82.0, y=38.0),
            PlayerToken(id="p11", name="Right Forward", number=7, role="ST", x=82.0, y=62.0),
        ],
    ),
    FormationPreset(
        id="5-3-2",
        name="5-3-2 Low Block Counter",
        description="Resilient defensive structure protecting the penalty box with quick transitions.",
        players=[
            PlayerToken(id="p1", name="Goalkeeper", number=1, role="GK", x=5.0, y=50.0),
            PlayerToken(id="p2", name="Left Wingback", number=3, role="LWB", x=28.0, y=10.0),
            PlayerToken(id="p3", name="Left CB", number=6, role="CB", x=20.0, y=28.0),
            PlayerToken(id="p4", name="Central CB", number=2, role="CB", x=17.0, y=50.0),
            PlayerToken(id="p5", name="Right CB", number=12, role="CB", x=20.0, y=72.0),
            PlayerToken(id="p6", name="Right Wingback", number=4, role="RWB", x=28.0, y=90.0),
            PlayerToken(id="p7", name="Left CM", number=41, role="CM", x=48.0, y=30.0),
            PlayerToken(id="p8", name="Anchor Mid", number=5, role="CM", x=42.0, y=50.0),
            PlayerToken(id="p9", name="Right CM", number=8, role="CM", x=48.0, y=70.0),
            PlayerToken(id="p10", name="Counter Forward 1", number=11, role="ST", x=80.0, y=38.0),
            PlayerToken(id="p11", name="Counter Forward 2", number=7, role="ST", x=80.0, y=62.0),
        ],
    ),
]

# Read-only cold-start boards used ONLY when tactical_boards table has 0 rows
DEMO_BOARDS: List[TacticalBoardResponse] = [
    TacticalBoardResponse(
        id="tb_arsenal_highpress",
        user_id="usr_seed_alex",
        author_name="GoonerAlex",
        author_club_id="arsenal",
        title="Arteta 4-3-3 High Press & Half-Space Overloads",
        formation="4-3-3",
        lineup=PRESETS[0].players,
        annotations=[
            {"id": "a1", "type": "run", "from_x": 76.0, "from_y": 84.0, "to_x": 88.0, "to_y": 68.0, "label": "Inside cut"},
            {"id": "a2", "type": "pass", "from_x": 54.0, "from_y": 70.0, "to_x": 76.0, "to_y": 84.0, "label": "Through ball"},
            {"id": "a3", "type": "press", "from_x": 82.0, "from_y": 50.0, "to_x": 92.0, "to_y": 50.0, "label": "Front pressing"},
        ],
        tactical_notes="Isolate Saka 1v1 on the right flank while Ødegaard and White generate the overlapping triangle.",
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
    ),
    TacticalBoardResponse(
        id="tb_arsenal_lowblock_breaker",
        user_id="usr_seed_clock",
        author_name="ClockEndTactician",
        author_club_id="arsenal",
        title="Arteta 3-2-4-1 Inverted Low-Block Breaker",
        formation="4-2-3-1",
        lineup=PRESETS[1].players,
        annotations=[
            {"id": "ra1", "type": "run", "from_x": 72.0, "from_y": 18.0, "to_x": 86.0, "to_y": 35.0, "label": "Martinelli diagonal cut"},
            {"id": "ra2", "type": "pass", "from_x": 58.0, "from_y": 50.0, "to_x": 84.0, "to_y": 50.0, "label": "Through ball to Havertz"},
        ],
        tactical_notes="Invert Timber into the central axis alongside Rice to create a 3-2 rest defense and prevent counter-attacks.",
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
    ),
    TacticalBoardResponse(
        id="tb_arsenal_derby_lockdown",
        user_id="usr_seed_nb",
        author_name="NorthBankFan",
        author_club_id="arsenal",
        title="Arteta 4-4-2 Compact Mid-Block & Transition Trap",
        formation="4-4-2",
        lineup=PRESETS[3].players,
        annotations=[
            {"id": "da1", "type": "press", "from_x": 46.0, "from_y": 38.0, "to_x": 52.0, "to_y": 38.0, "label": "Rice ball contest"},
            {"id": "da2", "type": "run", "from_x": 52.0, "from_y": 85.0, "to_x": 78.0, "to_y": 85.0, "label": "Saka transition sprint"},
        ],
        tactical_notes="Two ultra-narrow banks of four deny central penetration, forcing rivals into wide crosses dealt with by Saliba and Gabriel.",
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6),
    ),
]


def _serialize_board(board: TacticalBoard) -> TacticalBoardResponse:
    return TacticalBoardResponse(
        id=board.id,
        user_id=board.user_id,
        author_name=board.author_name,
        author_club_id=board.author_club_id,
        title=board.title,
        formation=board.formation,
        lineup=board.lineup,
        annotations=board.annotations or [],
        tactical_notes=board.tactical_notes,
        is_public=board.is_public,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@router.get("/formations/presets", response_model=List[FormationPreset])
async def get_formation_presets():
    """Returns canonical formation presets and coordinate maps for standard tactical systems."""
    return PRESETS


@router.post("", response_model=TacticalBoardResponse)
async def create_tactical_board(
    payload: TacticalBoardCreate,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Saves a new tactical board configuration owned by the authenticated user."""
    board_id = f"tb_{uuid.uuid4().hex[:10]}"
    now = datetime.datetime.now(datetime.timezone.utc)

    lineup_dict = [p.model_dump() for p in payload.lineup]
    annotations_dict = [a.model_dump() for a in payload.annotations] if payload.annotations else []
    author_name = (
        current_user.display_name
        if not payload.author_name or payload.author_name == "Supporter"
        else payload.author_name
    )
    author_club_id = payload.author_club_id or current_user.club_id or "arsenal"

    new_board = TacticalBoard(
        id=board_id,
        user_id=current_user.id,
        author_name=author_name,
        author_club_id=author_club_id,
        title=payload.title,
        formation=payload.formation,
        lineup=lineup_dict,
        annotations=annotations_dict,
        tactical_notes=payload.tactical_notes,
        is_public=payload.is_public,
        created_at=now,
        updated_at=now,
    )
    db.add(new_board)
    await db.commit()
    await db.refresh(new_board)

    return _serialize_board(new_board)


@router.get("", response_model=List[TacticalBoardResponse])
async def list_tactical_boards(
    optional_user: OptionalUserDep,
    club_id: Optional[str] = Query(None, description="Filter by club ID"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Lists public community tactical boards (plus the authenticated user's private boards)."""
    total_in_db = (await db.execute(select(func.count(TacticalBoard.id)))).scalar() or 0
    if total_in_db == 0:
        if club_id:
            return [b for b in DEMO_BOARDS if b.author_club_id == club_id][:limit]
        return DEMO_BOARDS[:limit]

    visibility_filter = (
        or_(TacticalBoard.is_public == True, TacticalBoard.user_id == optional_user.id)
        if optional_user
        else (TacticalBoard.is_public == True)
    )
    stmt = (
        select(TacticalBoard)
        .where(visibility_filter)
        .order_by(desc(TacticalBoard.created_at))
        .limit(limit)
    )
    if club_id:
        stmt = stmt.where(TacticalBoard.author_club_id == club_id)

    res = await db.execute(stmt)
    boards = res.scalars().all()
    return [_serialize_board(b) for b in boards]


@router.get("/{board_id}", response_model=TacticalBoardResponse)
async def get_tactical_board(
    board_id: str,
    optional_user: OptionalUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a single tactical board by ID."""
    stmt = select(TacticalBoard).where(TacticalBoard.id == board_id)
    board = (await db.execute(stmt)).scalar_one_or_none()
    if board:
        if not board.is_public and (not optional_user or board.user_id != optional_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this tactical board")
        return _serialize_board(board)

    total_in_db = (await db.execute(select(func.count(TacticalBoard.id)))).scalar() or 0
    if total_in_db == 0:
        found = next((b for b in DEMO_BOARDS if b.id == board_id), None)
        if found:
            return found

    raise HTTPException(status_code=404, detail="Tactical board not found")


@router.delete("/{board_id}")
async def delete_tactical_board(
    board_id: str,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Delete a tactical board owned by the authenticated user."""
    stmt = select(TacticalBoard).where(TacticalBoard.id == board_id)
    board = (await db.execute(stmt)).scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Tactical board not found")
    if board.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this tactical board")

    await db.delete(board)
    await db.commit()
    return {"status": "deleted", "id": board_id}
