import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.models.insight import Insight
from app.models.terrace import Post, PostReaction
from app.models.predictions import Prediction
from app.schemas.supporters import SupporterProfileResponse, SupporterStats
from app.schemas.insight import InsightResponse
from app.schemas.terrace import PostResponse
import json

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
        created_at=ins.created_at
    )

@router.get("/{username}", response_model=SupporterProfileResponse)
async def get_supporter_profile(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full public supporter profile, stats, published insights, and debates."""
    # Find insights by author_name
    ins_stmt = (
        select(Insight)
        .where(func.lower(Insight.author_name) == username.lower())
        .order_by(Insight.created_at.desc())
        .limit(6)
    )
    ins_res = await db.execute(ins_stmt)
    insights = [serialize_insight(i) for i in ins_res.scalars().all()]

    # Find posts by author_name
    post_stmt = (
        select(Post)
        .options(selectinload(Post.insight), selectinload(Post.reactions), selectinload(Post.comments))
        .where(func.lower(Post.author_name) == username.lower())
        .order_by(Post.created_at.desc())
        .limit(6)
    )
    post_res = await db.execute(post_stmt)
    posts = post_res.scalars().all()

    serialized_posts = []
    total_cheers = 0
    fav_club = "arsenal"
    for p in posts:
        total_cheers += len(p.reactions)
        if p.author_club_id:
            fav_club = p.author_club_id
        serialized_posts.append(
            PostResponse(
                id=p.id,
                author_id=p.author_id,
                author_name=p.author_name,
                author_club_id=p.author_club_id,
                club_id=p.club_id,
                content=p.content,
                insight_id=p.insight_id,
                insight=serialize_insight(p.insight) if p.insight else None,
                created_at=p.created_at,
                reactions_count=len(p.reactions),
                comments_count=len(p.comments),
                user_reacted=False
            )
        )

    # Prediction stats
    pred_stmt = select(Prediction).where(func.lower(Prediction.user_name) == username.lower())
    p_res = await db.execute(pred_stmt)
    preds = p_res.scalars().all()
    points = sum(p.points_awarded or 0 for p in preds)

    # Infer club affiliation if demo username
    uname_lower = username.lower()
    if "madrid" in uname_lower or "carlos" in uname_lower:
        fav_club = "real-madrid"
    elif "barca" in uname_lower or "cule" in uname_lower:
        fav_club = "barcelona"
    elif "milan" in uname_lower or "rossoneri" in uname_lower:
        fav_club = "milan"

    stats = SupporterStats(
        prediction_points=points if preds else 28,
        prediction_rank=1 if points > 20 else 3,
        total_predictions=len(preds) if preds else 14,
        exact_scores=len([p for p in preds if p.points_awarded == 3]) if preds else 6,
        insights_published=len(insights),
        posts_count=len(posts),
        cheers_received=total_cheers
    )

    return SupporterProfileResponse(
        user_id=f"usr_{username.lower()}",
        username=username,
        display_name=username,
        favorite_club_id=fav_club,
        bio=f"Dedicated {fav_club.capitalize()} supporter analyzing tactics and debating match evidence.",
        joined_at=datetime.datetime.utcnow() - datetime.timedelta(days=90),
        stats=stats,
        featured_insights=insights,
        recent_posts=serialized_posts
    )
