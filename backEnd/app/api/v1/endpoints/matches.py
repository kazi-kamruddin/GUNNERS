from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from typing import List, Optional
import datetime
from app.core.database import get_db
from app.models.football import Match, Club, SyncRun
from app.schemas.analytics import (
    MatchResponse,
    MatchSummaryResponse,
    SyncStatusResponse,
    AnalyticsQueryRequest,
    AnalyticsResponse
)
from app.services.analytics import AnalyticsEngine

router = APIRouter()

@router.get("", response_model=List[MatchResponse])
async def get_matches(
    club_id: Optional[str] = Query(None, description="Filter matches involving this club"),
    competition_id: Optional[str] = Query(None, description="Filter by competition (PL, PD, SA, CL)"),
    season_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="SCHEDULED, FINISHED, etc."),
    order: Optional[str] = Query(None, description="asc or desc"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve normalized matches with optional filters."""
    filters = []
    if club_id:
        filters.append(or_(Match.home_team_id == club_id, Match.away_team_id == club_id))
    if competition_id:
        filters.append(Match.competition_id == competition_id)
    if season_id:
        filters.append(Match.season_id == season_id)
    if status:
        filters.append(Match.status == status)

    stmt = select(Match)
    if filters:
        stmt = stmt.where(and_(*filters))
    
    # Determine ordering
    if order == "asc" or (order is None and status == "SCHEDULED"):
        stmt = stmt.order_by(asc(Match.utc_date))
    else:
        stmt = stmt.order_by(desc(Match.utc_date))
        
    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/summary", response_model=MatchSummaryResponse)
async def get_match_summary(
    club_id: str = Query("arsenal", description="Club ID to summarize"),
    db: AsyncSession = Depends(get_db)
):
    """Get next fixture, latest result, recent form, and match counts for a club."""
    club_res = await db.execute(select(Club).where(Club.id == club_id))
    club = club_res.scalar_one_or_none()
    club_name = club.name if club else club_id.title()

    club_match_filter = or_(Match.home_team_id == club_id, Match.away_team_id == club_id)

    # Next upcoming fixture (earliest SCHEDULED)
    next_stmt = (
        select(Match)
        .where(and_(club_match_filter, Match.status == "SCHEDULED"))
        .order_by(asc(Match.utc_date))
        .limit(1)
    )
    next_res = await db.execute(next_stmt)
    next_fixture = next_res.scalar_one_or_none()

    # Latest finished match
    last_stmt = (
        select(Match)
        .where(and_(club_match_filter, Match.status == "FINISHED"))
        .order_by(desc(Match.utc_date))
        .limit(1)
    )
    last_res = await db.execute(last_stmt)
    last_result = last_res.scalar_one_or_none()

    # Recent form from last 5 completed matches
    form_stmt = (
        select(Match)
        .where(and_(club_match_filter, Match.status == "FINISHED"))
        .order_by(desc(Match.utc_date))
        .limit(5)
    )
    form_res = await db.execute(form_stmt)
    recent_matches = form_res.scalars().all()
    
    recent_form = []
    for m in recent_matches:
        if m.winner == "DRAW":
            recent_form.append("D")
        elif (m.winner == "HOME_TEAM" and m.home_team_id == club_id) or (m.winner == "AWAY_TEAM" and m.away_team_id == club_id):
            recent_form.append("W")
        else:
            recent_form.append("L")
    # Form read left-to-right from oldest to newest of the 5
    recent_form.reverse()

    # Counts
    comp_count_stmt = select(func.count(Match.id)).where(and_(club_match_filter, Match.status == "FINISHED"))
    sched_count_stmt = select(func.count(Match.id)).where(and_(club_match_filter, Match.status == "SCHEDULED"))
    
    total_completed = (await db.execute(comp_count_stmt)).scalar() or 0
    total_scheduled = (await db.execute(sched_count_stmt)).scalar() or 0

    return MatchSummaryResponse(
        club_id=club_id,
        club_name=club_name,
        next_fixture=next_fixture,
        last_result=last_result,
        recent_form=recent_form,
        total_completed=total_completed,
        total_scheduled=total_scheduled
    )

@router.get("/sync-status", response_model=SyncStatusResponse)
async def get_sync_status(
    db: AsyncSession = Depends(get_db)
):
    """Retrieve latest data pipeline synchronization status and freshness metadata."""
    stmt = select(SyncRun).order_by(desc(SyncRun.started_at)).limit(1)
    res = await db.execute(stmt)
    latest = res.scalar_one_or_none()

    if latest:
        return SyncStatusResponse(
            latest_sync=latest.completed_at or latest.started_at,
            status=latest.status,
            source=latest.source,
            matches_synced=latest.matches_synced,
            error_message=latest.error_message
        )

    return SyncStatusResponse(
        latest_sync=datetime.datetime.utcnow(),
        status="ACTIVE",
        source="football-data.org (cached baseline)",
        matches_synced=0,
        error_message=None
    )

@router.post("/query", response_model=AnalyticsResponse)
async def query_analytics(
    request: AnalyticsQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run validated, reproducible statistical analysis across eligible completed matches."""
    return await AnalyticsEngine.compute_analytics(db, request)
