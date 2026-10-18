import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.models.terrace import Post, PostComment, PostReaction
from app.models.insight import Insight
from app.schemas.terrace import (
    PostCreateRequest,
    PostResponse,
    CommentCreateRequest,
    CommentResponse,
    ReactionToggleRequest
)
from app.schemas.insight import InsightResponse

router = APIRouter()

def serialize_insight_response(ins: Optional[Insight]) -> Optional[InsightResponse]:
    if not ins:
        return None
    try:
        parsed_snap = json.loads(ins.snapshot)
    except Exception:
        parsed_snap = {}
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
        snapshot=parsed_snap,
        is_public=ins.is_public,
        created_at=ins.created_at
    )

@router.get("/posts", response_model=List[PostResponse])
async def list_posts(
    club_id: Optional[str] = Query(None, description="Filter by club or 'global'"),
    current_user_id: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List terrace community posts with reaction counts, comments count, and attached insights."""
    stmt = (
        select(Post)
        .options(
            selectinload(Post.insight),
            selectinload(Post.comments),
            selectinload(Post.reactions)
        )
        .order_by(desc(Post.created_at))
    )

    if club_id and club_id != "global":
        stmt = stmt.where(Post.club_id == club_id)

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    posts = res.scalars().all()

    result: List[PostResponse] = []
    for p in posts:
        reactions_cnt = len(p.reactions)
        comments_cnt = len(p.comments)
        user_reacted = any(r.user_id == current_user_id for r in p.reactions) if current_user_id else False

        result.append(
            PostResponse(
                id=p.id,
                author_id=p.author_id,
                author_name=p.author_name,
                author_club_id=p.author_club_id,
                club_id=p.club_id,
                content=p.content,
                insight_id=p.insight_id,
                insight=serialize_insight_response(p.insight),
                created_at=p.created_at,
                reactions_count=reactions_cnt,
                comments_count=comments_cnt,
                user_reacted=user_reacted
            )
        )

    return result

@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    request: PostCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Publish a post to the global feed or a specific club terrace with optional insight attachment."""
    # Verify insight exists if provided
    attached_insight = None
    if request.insight_id:
        ins_res = await db.execute(select(Insight).where(Insight.id == request.insight_id))
        attached_insight = ins_res.scalar_one_or_none()
        if not attached_insight:
            raise HTTPException(status_code=400, detail="Attached insight not found")

    post_id = f"post_{uuid.uuid4().hex[:12]}"
    new_post = Post(
        id=post_id,
        author_id=None,
        author_name=request.author_name,
        author_club_id=request.author_club_id,
        club_id=request.club_id if request.club_id != "global" else None,
        content=request.content,
        insight_id=request.insight_id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return PostResponse(
        id=new_post.id,
        author_id=new_post.author_id,
        author_name=new_post.author_name,
        author_club_id=new_post.author_club_id,
        club_id=new_post.club_id,
        content=new_post.content,
        insight_id=new_post.insight_id,
        insight=serialize_insight_response(attached_insight),
        created_at=new_post.created_at,
        reactions_count=0,
        comments_count=0,
        user_reacted=False
    )

@router.post("/posts/{post_id}/react")
async def toggle_reaction(
    post_id: str,
    request: ReactionToggleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Toggle a reaction on a post."""
    post_res = await db.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_stmt = select(PostReaction).where(
        and_(
            PostReaction.post_id == post_id,
            PostReaction.user_id == request.user_id,
            PostReaction.reaction_type == request.reaction_type
        )
    )
    existing_res = await db.execute(existing_stmt)
    existing = existing_res.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        action = "removed"
    else:
        new_reaction = PostReaction(
            id=f"rxn_{uuid.uuid4().hex[:10]}",
            post_id=post_id,
            user_id=request.user_id,
            reaction_type=request.reaction_type
        )
        db.add(new_reaction)
        action = "added"

    await db.commit()

    count_stmt = select(func.count(PostReaction.id)).where(PostReaction.post_id == post_id)
    total_count = (await db.execute(count_stmt)).scalar() or 0

    return {
        "action": action,
        "reaction_type": request.reaction_type,
        "total_reactions": total_count
    }

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    post_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List comments under a post."""
    stmt = select(PostComment).where(PostComment.post_id == post_id).order_by(PostComment.created_at.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: str,
    request: CommentCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add a comment under a post."""
    post_res = await db.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_id = f"cmt_{uuid.uuid4().hex[:10]}"
    new_comment = PostComment(
        id=comment_id,
        post_id=post_id,
        author_id=None,
        author_name=request.author_name,
        author_club_id=request.author_club_id,
        content=request.content
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment
