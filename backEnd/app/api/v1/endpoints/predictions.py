import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional
from app.core.database import get_db
from app.models.predictions import Prediction
from app.models.football import Match
from app.schemas.predictions import (
    PredictionCreateRequest,
    PredictionResponse,
    UpcomingMatchPredictionItem,
    LeaderboardEntry
)
from app.schemas.analytics import MatchResponse

router = APIRouter()

# Default seed leaderboard entries for vibrant community feeling
DEFAULT_LEADERBOARD: List[dict] = [
    {
        "rank": 1,
        "user_id": "usr_alex_arsenal",
        "user_name": "GoonerAlex",
        "user_club_id": "arsenal",
        "total_points": 28,
        "predictions_count": 14,
        "exact_scores": 6,
        "correct_outcomes": 10,
        "accuracy_rate": 71.4
    },
    {
        "rank": 2,
        "user_id": "usr_carlos_madrid",
        "user_name": "MadridistaCarlos",
        "user_club_id": "real-madrid",
        "total_points": 24,
        "predictions_count": 13,
        "exact_scores": 5,
        "correct_outcomes": 9,
        "accuracy_rate": 69.2
    },
    {
        "rank": 3,
        "user_id": "usr_marc_barca",
        "user_name": "CuleMarc",
        "user_club_id": "barcelona",
        "total_points": 21,
        "predictions_count": 12,
        "exact_scores": 4,
        "correct_outcomes": 9,
        "accuracy_rate": 75.0
    },
    {
        "rank": 4,
        "user_id": "usr_paolo_milan",
        "user_name": "RossoneriPaolo",
        "user_club_id": "milan",
        "total_points": 18,
        "predictions_count": 12,
        "exact_scores": 3,
        "correct_outcomes": 9,
        "accuracy_rate": 75.0
    }
]

def format_prediction_response(p: Prediction) -> PredictionResponse:
    return PredictionResponse(
        id=p.id,
        user_id=p.user_id,
        user_name=p.user_name,
        user_club_id=p.user_club_id,
        match_id=p.match_id,
        predicted_home_score=p.predicted_home_score,
        predicted_away_score=p.predicted_away_score,
        points_awarded=p.points_awarded,
        created_at=p.created_at
    )

@router.get("/upcoming", response_model=List[UpcomingMatchPredictionItem])
async def get_upcoming_matches_for_prediction(
    user_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve upcoming matches open for score prediction along with user's prediction."""
    # Find SCHEDULED matches from DB
    stmt = select(Match).where(Match.status == "SCHEDULED").order_by(Match.utc_date.asc()).limit(10)
    res = await db.execute(stmt)
    scheduled_matches = res.scalars().all()

    # If no scheduled matches in DB, provide standard fixtures
    if not scheduled_matches:
        now = datetime.datetime.utcnow()
        mock_matches = [
            Match(
                id="match_pred_1",
                competition_id="PL",
                competition_name="Premier League",
                season_id="2024-2025-PL",
                home_team_id="arsenal",
                home_team_name="Arsenal FC",
                home_team_crest="https://crests.football-data.org/57.png",
                away_team_id="nottingham-forest",
                away_team_name="Nottingham Forest FC",
                away_team_crest="https://crests.football-data.org/351.png",
                matchday=12,
                utc_date=now + datetime.timedelta(days=2),
                status="SCHEDULED",
                venue="Emirates Stadium"
            ),
            Match(
                id="match_pred_2",
                competition_id="PD",
                competition_name="La Liga",
                season_id="2024-2025-PD",
                home_team_id="real-madrid",
                home_team_name="Real Madrid CF",
                home_team_crest="https://crests.football-data.org/86.png",
                away_team_id="getafe",
                away_team_name="Getafe CF",
                away_team_crest="https://crests.football-data.org/82.png",
                matchday=13,
                utc_date=now + datetime.timedelta(days=3),
                status="SCHEDULED",
                venue="Santiago Bernabéu"
            ),
            Match(
                id="match_pred_3",
                competition_id="SA",
                competition_name="Serie A",
                season_id="2024-2025-SA",
                home_team_id="milan",
                home_team_name="AC Milan",
                home_team_crest="https://crests.football-data.org/98.png",
                away_team_id="juventus",
                away_team_name="Juventus FC",
                away_team_crest="https://crests.football-data.org/109.png",
                matchday=13,
                utc_date=now + datetime.timedelta(days=4),
                status="SCHEDULED",
                venue="San Siro"
            )
        ]
        scheduled_matches = mock_matches

    # Fetch user's existing predictions if user_id is provided
    user_predictions_map = {}
    if user_id:
        pred_stmt = select(Prediction).where(Prediction.user_id == user_id)
        p_res = await db.execute(pred_stmt)
        for p in p_res.scalars().all():
            user_predictions_map[p.match_id] = format_prediction_response(p)

    items = []
    for m in scheduled_matches:
        match_resp = MatchResponse.model_validate(m)
        existing_pred = user_predictions_map.get(m.id)
        items.append(
            UpcomingMatchPredictionItem(
                match=match_resp,
                user_prediction=existing_pred,
                can_predict=True,
                total_predictions_count=12
            )
        )
    return items

@router.post("", response_model=PredictionResponse, status_code=201)
async def submit_prediction(
    request: PredictionCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Submit or update a matchday score prediction."""
    # Check if prediction for this match and user already exists
    stmt = select(Prediction).where(
        and_(
            Prediction.user_id == request.user_id,
            Prediction.match_id == request.match_id
        )
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    if existing:
        existing.predicted_home_score = request.predicted_home_score
        existing.predicted_away_score = request.predicted_away_score
        existing.user_name = request.user_name
        existing.user_club_id = request.user_club_id
        await db.commit()
        await db.refresh(existing)
        return format_prediction_response(existing)

    new_pred = Prediction(
        id=f"pred_{uuid.uuid4().hex[:10]}",
        user_id=request.user_id,
        user_name=request.user_name,
        user_club_id=request.user_club_id,
        match_id=request.match_id,
        predicted_home_score=request.predicted_home_score,
        predicted_away_score=request.predicted_away_score,
        points_awarded=None
    )
    db.add(new_pred)
    await db.commit()
    await db.refresh(new_pred)
    return format_prediction_response(new_pred)

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_supporter_leaderboard(
    club_id: Optional[str] = Query(None, description="Filter leaderboard by club"),
    db: AsyncSession = Depends(get_db)
):
    """Get supporter prediction rankings and points."""
    # Group predictions by user_id to compute total points
    stmt = (
        select(
            Prediction.user_id,
            Prediction.user_name,
            Prediction.user_club_id,
            func.count(Prediction.id).label("total_preds"),
            func.coalesce(func.sum(Prediction.points_awarded), 0).label("total_points")
        )
        .group_by(Prediction.user_id, Prediction.user_name, Prediction.user_club_id)
        .order_by(desc("total_points"))
    )
    if club_id:
        stmt = stmt.where(Prediction.user_club_id == club_id)

    res = await db.execute(stmt)
    rows = res.all()

    if rows:
        result = []
        for rank, r in enumerate(rows, 1):
            preds_cnt = r.total_preds or 1
            points = int(r.total_points or 0)
            result.append(
                LeaderboardEntry(
                    rank=rank,
                    user_id=r.user_id,
                    user_name=r.user_name,
                    user_club_id=r.user_club_id,
                    total_points=points,
                    predictions_count=preds_cnt,
                    exact_scores=max(points // 3, 0),
                    correct_outcomes=preds_cnt,
                    accuracy_rate=round((points / (preds_cnt * 3)) * 100, 1) if preds_cnt else 0.0
                )
            )
        return result

    # Return baseline community entries
    entries = DEFAULT_LEADERBOARD
    if club_id:
        entries = [e for e in entries if e["user_club_id"] == club_id]
        # Re-index rank
        for i, e in enumerate(entries, 1):
            e["rank"] = i

    return [LeaderboardEntry(**e) for e in entries]
