import uuid
import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from app.core.database import get_db
from app.models.insight import Insight
from app.schemas.insight import InsightCreateRequest, InsightResponse
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsResponse
from app.services.analytics import AnalyticsEngine

router = APIRouter()

DEFAULT_INSIGHTS: List[InsightResponse] = [
    InsightResponse(
        id="ins_arsenal_winrate",
        user_id="usr_seed_alex",
        author_name="GoonerAlex",
        author_club_id="arsenal",
        title="Arsenal Home Win Rate 2024/25",
        description="Emirates Stadium home record and defensive stability across all competitions.",
        metric="win_rate",
        team_ids=["arsenal"],
        venue="home",
        competition_id=None,
        chart_type="bar",
        snapshot={
            "metric": "win_rate",
            "formula": "(wins / matches_played) * 100",
            "venue_filter": "home",
            "series": [{
                "team_id": "arsenal",
                "team_name": "Arsenal FC",
                "matches_played": 6,
                "wins": 5,
                "draws": 1,
                "losses": 0,
                "clean_sheets": 3,
                "goals_for": 14,
                "goals_against": 4,
                "goal_difference": 10,
                "metric_value": 83.3,
                "unit": "%"
            }],
            "computed_at": datetime.datetime.utcnow().isoformat(),
            "disclaimer": "Calculated strictly across eligible completed matches."
        },
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    ),
    InsightResponse(
        id="ins_clasico_ppg",
        user_id="usr_seed_carlos",
        author_name="MadridistaCarlos",
        author_club_id="real-madrid",
        title="Real Madrid vs Barcelona PPG Comparison",
        description="Points per game comparison across current campaign matches.",
        metric="points_per_game",
        team_ids=["real-madrid", "barcelona"],
        venue="all",
        competition_id=None,
        chart_type="comparison",
        snapshot={
            "metric": "points_per_game",
            "formula": "((wins * 3) + draws) / matches_played",
            "venue_filter": "all",
            "series": [
                {
                    "team_id": "real-madrid",
                    "team_name": "Real Madrid CF",
                    "matches_played": 10,
                    "wins": 7,
                    "draws": 2,
                    "losses": 1,
                    "clean_sheets": 4,
                    "goals_for": 21,
                    "goals_against": 11,
                    "goal_difference": 10,
                    "metric_value": 2.3,
                    "unit": "ppg"
                },
                {
                    "team_id": "barcelona",
                    "team_name": "FC Barcelona",
                    "matches_played": 10,
                    "wins": 8,
                    "draws": 0,
                    "losses": 2,
                    "clean_sheets": 4,
                    "goals_for": 28,
                    "goals_against": 10,
                    "goal_difference": 18,
                    "metric_value": 2.4,
                    "unit": "ppg"
                }
            ],
            "computed_at": datetime.datetime.utcnow().isoformat(),
            "disclaimer": "Calculated strictly across eligible completed matches."
        },
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4)
    ),
    InsightResponse(
        id="ins_milan_derby",
        user_id="usr_seed_paolo",
        author_name="RossoneriPaolo",
        author_club_id="milan",
        title="AC Milan Defensive Resilience & Clean Sheets",
        description="Clean sheet performance and defensive metrics in Serie A.",
        metric="clean_sheet_rate",
        team_ids=["milan"],
        venue="all",
        competition_id=None,
        chart_type="bar",
        snapshot={
            "metric": "clean_sheet_rate",
            "formula": "(clean_sheets / matches_played) * 100",
            "venue_filter": "all",
            "series": [{
                "team_id": "milan",
                "team_name": "AC Milan",
                "matches_played": 9,
                "wins": 5,
                "draws": 2,
                "losses": 2,
                "clean_sheets": 4,
                "goals_for": 16,
                "goals_against": 9,
                "goal_difference": 7,
                "metric_value": 44.4,
                "unit": "%"
            }],
            "computed_at": datetime.datetime.utcnow().isoformat(),
            "disclaimer": "Calculated strictly across eligible completed matches."
        },
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6)
    ),
    InsightResponse(
        id="ins_big_four_xg",
        user_id="usr_seed_marc",
        author_name="CuleMarc",
        author_club_id="barcelona",
        title="Barcelona vs Real Madrid Goal Difference Comparison",
        description="Goal difference and attacking conversion comparison in La Liga 2024/25.",
        metric="goal_difference",
        team_ids=["barcelona", "real-madrid"],
        venue="all",
        competition_id=None,
        chart_type="comparison",
        snapshot={
            "metric": "goal_difference",
            "formula": "goals_for - goals_against",
            "venue_filter": "all",
            "series": [
                {
                    "team_id": "barcelona",
                    "team_name": "FC Barcelona",
                    "matches_played": 10,
                    "wins": 8,
                    "draws": 0,
                    "losses": 2,
                    "clean_sheets": 4,
                    "goals_for": 28,
                    "goals_against": 10,
                    "goal_difference": 18,
                    "metric_value": 18.0,
                    "unit": "gd"
                },
                {
                    "team_id": "real-madrid",
                    "team_name": "Real Madrid CF",
                    "matches_played": 10,
                    "wins": 7,
                    "draws": 2,
                    "losses": 1,
                    "clean_sheets": 4,
                    "goals_for": 21,
                    "goals_against": 11,
                    "goal_difference": 10,
                    "metric_value": 10.0,
                    "unit": "gd"
                }
            ],
            "computed_at": datetime.datetime.utcnow().isoformat(),
            "disclaimer": "Calculated strictly across eligible completed matches."
        },
        is_public=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=8)
    )
]

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
    if not response:
        total_in_db = (await db.execute(select(func.count(Insight.id)))).scalar() or 0
        if total_in_db == 0:
            fallback = list(DEFAULT_INSIGHTS)
            if club_id:
                fallback = [ins for ins in fallback if club_id in ins.team_ids or ins.author_club_id == club_id]
            return fallback[:limit]

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
        fallback = next((ins for ins in DEFAULT_INSIGHTS if ins.id == insight_id), None)
        if fallback:
            return fallback
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
