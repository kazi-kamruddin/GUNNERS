import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.core.database import get_db
from app.models.insight import Insight
from app.schemas.insight import InsightCreateRequest, InsightResponse
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsResponse
from app.services.analytics import AnalyticsEngine

router = APIRouter()

@router.post("", response_model=InsightResponse, status_code=201)
async def create_insight(
    request: InsightCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save an immutable, reproducible analytics insight."""
    # Ensure snapshot exists, compute if not provided
    snapshot = request.snapshot
    if not snapshot:
        analytics_query = AnalyticsQueryRequest(
            metric=request.metric,
            team_ids=request.team_ids,
            venue=request.venue,
            competition_id=request.competition_id
        )
        snapshot = await AnalyticsEngine.compute_analytics(db, analytics_query)

    insight_id = f"ins_{uuid.uuid4().hex[:12]}"
    serialized_snapshot = json.dumps(snapshot.model_dump(), default=str)

    new_insight = Insight(
        id=insight_id,
        user_id=None,
        author_name=request.author_name,
        author_club_id=request.author_club_id,
        title=request.title,
        description=request.description,
        metric=request.metric,
        team_ids=",".join(request.team_ids),
        venue=request.venue,
        competition_id=request.competition_id,
        chart_type=request.chart_type,
        snapshot=serialized_snapshot,
        is_public=True
    )

    db.add(new_insight)
    await db.commit()
    await db.refresh(new_insight)

    return InsightResponse(
        id=new_insight.id,
        user_id=new_insight.user_id,
        author_name=new_insight.author_name,
        author_club_id=new_insight.author_club_id,
        title=new_insight.title,
        description=new_insight.description,
        metric=new_insight.metric,
        team_ids=new_insight.team_ids.split(","),
        venue=new_insight.venue,
        competition_id=new_insight.competition_id,
        chart_type=new_insight.chart_type,
        snapshot=json.loads(new_insight.snapshot),
        is_public=new_insight.is_public,
        created_at=new_insight.created_at
    )

@router.get("", response_model=List[InsightResponse])
async def list_insights(
    limit: int = Query(20, ge=1, le=50),
    club_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve recent reproducible insights."""
    stmt = select(Insight).where(Insight.is_public == True).order_by(desc(Insight.created_at)).limit(limit)
    res = await db.execute(stmt)
    records = res.scalars().all()

    response = []
    for r in records:
        team_ids = r.team_ids.split(",")
        if club_id and club_id not in team_ids:
            continue
        try:
            parsed_snap = json.loads(r.snapshot)
        except Exception:
            parsed_snap = {}
        response.append(
            InsightResponse(
                id=r.id,
                user_id=r.user_id,
                author_name=r.author_name,
                author_club_id=r.author_club_id,
                title=r.title,
                description=r.description,
                metric=r.metric,
                team_ids=team_ids,
                venue=r.venue,
                competition_id=r.competition_id,
                chart_type=r.chart_type,
                snapshot=parsed_snap,
                is_public=r.is_public,
                created_at=r.created_at
            )
        )
    return response

@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve single insight by ID."""
    stmt = select(Insight).where(Insight.id == insight_id)
    res = await db.execute(stmt)
    insight = res.scalar_one_or_none()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    return InsightResponse(
        id=insight.id,
        user_id=insight.user_id,
        author_name=insight.author_name,
        author_club_id=insight.author_club_id,
        title=insight.title,
        description=insight.description,
        metric=insight.metric,
        team_ids=insight.team_ids.split(","),
        venue=insight.venue,
        competition_id=insight.competition_id,
        chart_type=insight.chart_type,
        snapshot=json.loads(insight.snapshot),
        is_public=insight.is_public,
        created_at=insight.created_at
    )
