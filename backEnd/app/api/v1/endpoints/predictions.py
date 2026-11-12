import uuid
import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, desc
from app.core.database import get_db
from app.core.security import CurrentUserDep, OptionalUserDep
from app.models.predictions import Prediction
from app.models.football import Club, Match
from app.schemas.predictions import (
    PredictionCreateRequest,
    PredictionResponse,
    UpcomingMatchPredictionItem,
    LeaderboardEntry,
    PredictionGradeResponse,
    PredictionHistoryItem,
)
from app.schemas.analytics import MatchResponse
from app.services.predictor_grading import _outcome_sign, grade_match_predictions

router = APIRouter()


def _to_utc(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _grade_prediction(pred: Prediction, match: Optional[Match]) -> tuple[int, bool, bool, bool]:
    """Return (points, is_exact, is_correct_outcome, is_graded)."""
    if pred.points_awarded is not None:
        pts = int(pred.points_awarded)
        return pts, pts == 3, pts >= 1, True

    if (
        match is not None
        and match.status == "FINISHED"
        and match.home_score is not None
        and match.away_score is not None
    ):
        if (
            pred.predicted_home_score == match.home_score
            and pred.predicted_away_score == match.away_score
        ):
            return 3, True, True, True
        if _outcome_sign(pred.predicted_home_score, pred.predicted_away_score) == _outcome_sign(
            match.home_score, match.away_score
        ):
            return 1, False, True, True
        return 0, False, False, True

    return 0, False, False, False


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
        created_at=p.created_at,
    )


@router.get("/upcoming", response_model=List[UpcomingMatchPredictionItem])
async def get_upcoming_matches_for_prediction(
    optional_user: OptionalUserDep,
    user_id: Optional[str] = Query(None),
    club_id: Optional[str] = Query(None, description="Optional club filter (e.g. arsenal)"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve scheduled matches from DB along with real prediction counts and kickoff lock status."""
    stmt = select(Match).where(Match.status == "SCHEDULED")
    if club_id:
        stmt = stmt.where(or_(Match.home_team_id == club_id, Match.away_team_id == club_id))
    stmt = stmt.order_by(Match.utc_date.asc()).limit(10)

    res = await db.execute(stmt)
    scheduled_matches = res.scalars().all()
    if not scheduled_matches:
        return []

    match_ids = [m.id for m in scheduled_matches]

    # Real SQL counts per match
    count_stmt = (
        select(Prediction.match_id, func.count(Prediction.id))
        .where(Prediction.match_id.in_(match_ids))
        .group_by(Prediction.match_id)
    )
    count_rows = (await db.execute(count_stmt)).all()
    counts_map: Dict[str, int] = {m_id: int(cnt) for m_id, cnt in count_rows}

    effective_user_id = optional_user.id if optional_user else user_id
    user_predictions_map: Dict[str, PredictionResponse] = {}
    if effective_user_id:
        pred_stmt = select(Prediction).where(
            and_(
                Prediction.user_id == effective_user_id,
                Prediction.match_id.in_(match_ids),
            )
        )
        p_res = await db.execute(pred_stmt)
        for p in p_res.scalars().all():
            user_predictions_map[p.match_id] = format_prediction_response(p)

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    items: List[UpcomingMatchPredictionItem] = []
    for m in scheduled_matches:
        match_resp = MatchResponse.model_validate(m)
        can_predict = m.status == "SCHEDULED" and _to_utc(m.utc_date) > now_utc
        items.append(
            UpcomingMatchPredictionItem(
                match=match_resp,
                user_prediction=user_predictions_map.get(m.id),
                can_predict=can_predict,
                total_predictions_count=counts_map.get(m.id, 0),
            )
        )
    return items


@router.post("", response_model=PredictionResponse, status_code=201)
async def submit_prediction(
    request: PredictionCreateRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Submit or update a matchday score prediction for the authenticated user."""
    match_res = await db.execute(select(Match).where(Match.id == request.match_id))
    match = match_res.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if match.status != "SCHEDULED" or _to_utc(match.utc_date) <= now_utc:
        raise HTTPException(
            status_code=400,
            detail="Match kickoff has passed; predictions are locked",
        )

    user_name = (
        current_user.display_name
        if not request.user_name or request.user_name == "Supporter"
        else request.user_name
    )
    user_club_id = request.user_club_id or current_user.club_id or "arsenal"

    stmt = select(Prediction).where(
        and_(
            Prediction.user_id == current_user.id,
            Prediction.match_id == request.match_id,
        )
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        existing.predicted_home_score = request.predicted_home_score
        existing.predicted_away_score = request.predicted_away_score
        existing.user_name = user_name
        existing.user_club_id = user_club_id
        await db.commit()
        await db.refresh(existing)
        return format_prediction_response(existing)

    new_pred = Prediction(
        id=f"pred_{uuid.uuid4().hex[:10]}",
        user_id=current_user.id,
        user_name=user_name,
        user_club_id=user_club_id,
        match_id=request.match_id,
        predicted_home_score=request.predicted_home_score,
        predicted_away_score=request.predicted_away_score,
        points_awarded=None,
    )
    db.add(new_pred)
    await db.commit()
    await db.refresh(new_pred)
    return format_prediction_response(new_pred)


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_supporter_leaderboard(
    club_id: Optional[str] = Query(None, description="Filter leaderboard by club"),
    season_id: Optional[str] = Query(
        None,
        description="Season filter (all, campaign YYYY-YYYY, or exact season_id)",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get supporter prediction rankings and points computed strictly from DB records."""
    stmt = (
        select(Prediction, Match)
        .outerjoin(Match, Prediction.match_id == Match.id)
        .order_by(Prediction.created_at.asc())
    )
    if club_id:
        stmt = stmt.where(Prediction.user_club_id == club_id)
    if season_id:
        cleaned_season = season_id.strip()
        if cleaned_season and cleaned_season.lower() != "all":
            if len(cleaned_season.split("-")) == 2:
                stmt = stmt.where(Match.season_id.like(f"{cleaned_season}-%"))
            else:
                stmt = stmt.where(Match.season_id == cleaned_season)

    rows = (await db.execute(stmt)).all()
    if not rows:
        return []

    aggregates: Dict[str, dict] = {}
    for pred, match in rows:
        pts, is_exact, is_correct, is_graded = _grade_prediction(pred, match)
        bucket = aggregates.get(pred.user_id)
        if not bucket:
            bucket = {
                "user_id": pred.user_id,
                "user_name": pred.user_name,
                "user_club_id": pred.user_club_id,
                "total_points": 0,
                "predictions_count": 0,
                "graded_count": 0,
                "exact_scores": 0,
                "correct_outcomes": 0,
            }
            aggregates[pred.user_id] = bucket

        bucket["user_name"] = pred.user_name
        bucket["user_club_id"] = pred.user_club_id
        bucket["total_points"] += pts
        bucket["predictions_count"] += 1
        if is_graded:
            bucket["graded_count"] += 1
        if is_exact:
            bucket["exact_scores"] += 1
        if is_correct:
            bucket["correct_outcomes"] += 1

    sorted_entries = sorted(
        aggregates.values(),
        key=lambda e: (
            -e["total_points"],
            -e["exact_scores"],
            -e["correct_outcomes"],
            e["user_name"].lower(),
        ),
    )

    result: List[LeaderboardEntry] = []
    for rank, entry in enumerate(sorted_entries, 1):
        graded = entry["graded_count"]
        accuracy = round((entry["correct_outcomes"] / graded) * 100, 1) if graded > 0 else 0.0
        result.append(
            LeaderboardEntry(
                rank=rank,
                user_id=entry["user_id"],
                user_name=entry["user_name"],
                user_club_id=entry["user_club_id"],
                total_points=entry["total_points"],
                predictions_count=entry["predictions_count"],
                exact_scores=entry["exact_scores"],
                correct_outcomes=entry["correct_outcomes"],
                accuracy_rate=accuracy,
            )
        )
    return result


@router.post("/grade/{match_id}", response_model=PredictionGradeResponse)
async def grade_match_predictions_endpoint(
    match_id: str,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Grade all ungraded predictions for a finished match and notify supporters."""
    match_res = await db.execute(select(Match).where(Match.id == match_id))
    match = match_res.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "FINISHED" or match.home_score is None or match.away_score is None:
        raise HTTPException(
            status_code=400,
            detail="Match must be FINISHED with final scores to grade predictions",
        )

    graded_count = await grade_match_predictions(db, match)
    await db.commit()
    return PredictionGradeResponse(match_id=match.id, graded_count=graded_count)


@router.get("/history", response_model=List[PredictionHistoryItem])
async def get_prediction_history(
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated supporter's prediction history joined with match and club names."""
    stmt = (
        select(Prediction, Match)
        .outerjoin(Match, Prediction.match_id == Match.id)
        .where(Prediction.user_id == current_user.id)
        .order_by(desc(Prediction.created_at))
    )
    rows = (await db.execute(stmt)).all()
    if not rows:
        return []

    team_ids = {
        tid
        for _, match in rows
        if match is not None
        for tid in (match.home_team_id, match.away_team_id)
        if tid
    }
    club_names: Dict[str, str] = {}
    if team_ids:
        club_res = await db.execute(select(Club).where(Club.id.in_(team_ids)))
        club_names = {c.id: c.name for c in club_res.scalars().all()}

    items: List[PredictionHistoryItem] = []
    for pred, match in rows:
        status_label = "GRADED" if pred.points_awarded is not None else "PENDING"
        if match is not None:
            home_team = club_names.get(match.home_team_id) or (
                match.home_team_name
                if match.home_team_name and match.home_team_name != "Home Team"
                else match.home_team_id
            )
            away_team = club_names.get(match.away_team_id) or (
                match.away_team_name
                if match.away_team_name and match.away_team_name != "Away Team"
                else match.away_team_id
            )
            items.append(
                PredictionHistoryItem(
                    id=pred.id,
                    match_id=pred.match_id,
                    predicted_home_score=pred.predicted_home_score,
                    predicted_away_score=pred.predicted_away_score,
                    points_awarded=pred.points_awarded,
                    status=status_label,
                    created_at=pred.created_at,
                    home_team=home_team,
                    away_team=away_team,
                    home_score=match.home_score,
                    away_score=match.away_score,
                    utc_date=match.utc_date,
                    match_status=match.status,
                    competition=match.competition_name or match.competition_id or "Premier League",
                )
            )
        else:
            items.append(
                PredictionHistoryItem(
                    id=pred.id,
                    match_id=pred.match_id,
                    predicted_home_score=pred.predicted_home_score,
                    predicted_away_score=pred.predicted_away_score,
                    points_awarded=pred.points_awarded,
                    status=status_label,
                    created_at=pred.created_at,
                    home_team="Home Team",
                    away_team="Away Team",
                    home_score=None,
                    away_score=None,
                    utc_date=pred.created_at,
                    match_status="UNKNOWN",
                    competition="Unknown",
                )
            )
    return items
