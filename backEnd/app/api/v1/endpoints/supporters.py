import datetime
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.profile import Profile
from app.models.insight import Insight
from app.models.terrace import Post
from app.models.predictions import Prediction
from app.models.football import Match
from app.schemas.supporters import SupporterProfileResponse, SupporterStats
from app.schemas.insight import InsightResponse
from app.schemas.terrace import PostResponse
from app.api.v1.endpoints.predictions import _grade_prediction
from app.api.v1.endpoints.terrace import serialize_tactical_board_response

router = APIRouter()


def serialize_insight(ins: Insight) -> InsightResponse:
    try:
        snap = json.loads(ins.snapshot)
    except Exception:
        snap = {}
    return InsightResponse(
        id=ins.id,
        user_id=ins.user_id,
        author_name=ins.author_name,
        author_club_id=ins.author_club_id,
        title=ins.title,
        description=ins.description,
        metric=ins.metric,
        team_ids=ins.team_ids.split(","),
        venue=ins.venue,
        competition_id=ins.competition_id,
        chart_type=ins.chart_type,
        snapshot=snap,
        is_public=ins.is_public,
        created_at=ins.created_at,
    )


async def _compute_prediction_rank(db: AsyncSession, target_user_ids: set[str]) -> int:
    """Compute real 1-based prediction rank among all predictors in DB, or 0 if none."""
    if not target_user_ids:
        return 0
    rows = (
        await db.execute(
            select(Prediction, Match).outerjoin(Match, Prediction.match_id == Match.id)
        )
    ).all()
    if not rows:
        return 0

    scores: Dict[str, tuple[int, int]] = {}
    for pred, match in rows:
        pts, is_exact, _, _ = _grade_prediction(pred, match)
        prev_pts, prev_exact = scores.get(pred.user_id, (0, 0))
        scores[pred.user_id] = (prev_pts + pts, prev_exact + (1 if is_exact else 0))

    if not any(uid in scores for uid in target_user_ids):
        return 0

    ranked = sorted(scores.items(), key=lambda item: (-item[1][0], -item[1][1], item[0]))
    for idx, (uid, _) in enumerate(ranked, 1):
        if uid in target_user_ids:
            return idx
    return 0


@router.get("/{username}", response_model=SupporterProfileResponse)
async def get_supporter_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve public supporter profile, real DB stats, published insights, and debates."""
    uname_lower = username.lower()

    profile = (
        await db.execute(select(Profile).where(func.lower(Profile.username) == uname_lower))
    ).scalar_one_or_none()

    # Insights authored by this supporter
    ins_filter = (
        or_(Insight.user_id == profile.id, func.lower(Insight.author_name) == uname_lower)
        if profile
        else (func.lower(Insight.author_name) == uname_lower)
    )
    ins_res = await db.execute(
        select(Insight).where(ins_filter).order_by(Insight.created_at.desc())
    )
    insights_all = ins_res.scalars().all()
    featured_insights = [serialize_insight(i) for i in insights_all[:6]]

    # Posts authored by this supporter
    post_filter = (
        or_(Post.author_id == profile.id, func.lower(Post.author_name) == uname_lower)
        if profile
        else (func.lower(Post.author_name) == uname_lower)
    )
    post_res = await db.execute(
        select(Post)
        .options(
            selectinload(Post.insight),
            selectinload(Post.tactical_board),
            selectinload(Post.reactions),
            selectinload(Post.comments),
        )
        .where(post_filter)
        .order_by(Post.created_at.desc())
    )
    posts_all = post_res.scalars().all()

    total_cheers = sum(len(p.reactions) for p in posts_all)
    serialized_posts: List[PostResponse] = []
    for p in posts_all[:6]:
        serialized_posts.append(
            PostResponse(
                id=p.id,
                author_id=p.author_id,
                author_name=p.author_name,
                author_club_id=p.author_club_id,
                club_id=p.club_id,
                content=p.content,
                image_url=p.image_url,
                insight_id=p.insight_id,
                insight=serialize_insight(p.insight) if p.insight else None,
                tactical_board_id=p.tactical_board_id,
                tactical_board=serialize_tactical_board_response(p.tactical_board),
                created_at=p.created_at,
                reactions_count=len(p.reactions),
                comments_count=len(p.comments),
                user_reacted=False,
            )
        )

    # Predictions for this supporter
    pred_filter = (
        or_(Prediction.user_id == profile.id, func.lower(Prediction.user_name) == uname_lower)
        if profile
        else (func.lower(Prediction.user_name) == uname_lower)
    )
    pred_rows = (
        await db.execute(
            select(Prediction, Match)
            .outerjoin(Match, Prediction.match_id == Match.id)
            .where(pred_filter)
        )
    ).all()

    if not profile and not insights_all and not posts_all and not pred_rows:
        raise HTTPException(status_code=404, detail="Supporter not found")

    points = 0
    exact_scores = 0
    pred_user_ids: set[str] = set()
    for pred, match in pred_rows:
        pts, is_exact, _, _ = _grade_prediction(pred, match)
        points += pts
        if is_exact:
            exact_scores += 1
        pred_user_ids.add(pred.user_id)

    if profile:
        pred_user_ids.add(profile.id)

    prediction_rank = await _compute_prediction_rank(db, pred_user_ids) if pred_rows else 0

    resolved_user_id: Optional[str] = profile.id if profile else None
    if not resolved_user_id and insights_all and insights_all[0].user_id:
        resolved_user_id = insights_all[0].user_id
    if not resolved_user_id and posts_all and posts_all[0].author_id:
        resolved_user_id = posts_all[0].author_id
    if not resolved_user_id and pred_rows:
        resolved_user_id = pred_rows[0][0].user_id
    if not resolved_user_id:
        resolved_user_id = f"usr_{uname_lower}"

    resolved_club = (
        profile.favorite_club_id
        if profile and profile.favorite_club_id
        else (
            posts_all[0].author_club_id
            if posts_all
            else (insights_all[0].author_club_id if insights_all else "arsenal")
        )
    )
    resolved_username = (profile.username if profile and profile.username else username)
    resolved_display_name = (
        profile.display_name
        if profile and profile.display_name
        else (
            posts_all[0].author_name
            if posts_all
            else (insights_all[0].author_name if insights_all else resolved_username)
        )
    )
    resolved_joined = (
        profile.created_at
        if profile and profile.created_at
        else (
            posts_all[-1].created_at
            if posts_all
            else (
                insights_all[-1].created_at
                if insights_all
                else datetime.datetime.now(datetime.timezone.utc)
            )
        )
    )

    stats = SupporterStats(
        prediction_points=points,
        prediction_rank=prediction_rank,
        total_predictions=len(pred_rows),
        exact_scores=exact_scores,
        insights_published=len(insights_all),
        posts_count=len(posts_all),
        cheers_received=total_cheers,
    )

    return SupporterProfileResponse(
        user_id=resolved_user_id,
        username=resolved_username,
        display_name=resolved_display_name,
        avatar_url=profile.avatar_url if profile else None,
        favorite_club_id=resolved_club,
        bio=profile.bio if profile else None,
        joined_at=resolved_joined,
        stats=stats,
        featured_insights=featured_insights,
        recent_posts=serialized_posts,
    )
