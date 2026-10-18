from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from typing import List, Optional
from app.core.database import get_db
from app.models.football import Match, Club
from app.schemas.analytics import MatchResponse, AnalyticsQueryRequest, AnalyticsResponse
from app.services.analytics import AnalyticsEngine

router = APIRouter()

@router.get("", response_model=List[MatchResponse])
async def get_matches(
    club_id: Optional[str] = Query(None, description="Filter matches involving this club"),
    competition_id: Optional[str] = Query(None),
    season_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="SCHEDULED, FINISHED, etc."),
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
    
    stmt = stmt.order_by(desc(Match.utc_date)).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/query", response_model=AnalyticsResponse)
async def query_analytics(
    request: AnalyticsQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run validated, reproducible statistical analysis across eligible completed matches."""
    return await AnalyticsEngine.compute_analytics(db, request)
