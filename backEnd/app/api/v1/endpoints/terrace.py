import uuid
import json
import re
import datetime
from collections import Counter
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.core.security import CurrentUserDep, OptionalUserDep
from app.models.terrace import Post, PostComment, PostReaction
from app.models.insight import Insight
from app.models.tactics import TacticalBoard
from app.services.notifications import create_notification
from app.schemas.terrace import (
    PostCreateRequest,
    PostResponse,
    CommentCreateRequest,
    CommentResponse,
    ReactionToggleRequest,
)
from app.schemas.insight import InsightResponse
from app.schemas.tactics import TacticalBoardResponse

router = APIRouter()

_HASHTAG_RE = re.compile(r"#([A-Za-z0-9_]+)")

# Curated fallback posts for instant cold-start resilience
DEFAULT_POSTS: List[PostResponse] = [
    PostResponse(
        id="post_seed_1",
        author_id="usr_seed_alex",
        author_name="GoonerAlex",
        author_club_id="arsenal",
        club_id="arsenal",
        content="Our defensive compactness and high press structure at the Emirates have been elite this season. Backed up with reproducible Data Lab numbers: 83.3% home win rate! Check the attached tactical blueprint for how we isolate Saka on the right wing. #NorthLondonDerby #Tactics",
        image_url="https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=800&q=80",
        insight_id="ins_arsenal_winrate",
        tactical_board_id="tb_arsenal_highpress",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        reactions_count=28,
        comments_count=4,
        user_reacted=False,
    ),
    PostResponse(
        id="post_seed_2",
        author_id="usr_seed_ana",
        author_name="ArsenalAnalytics",
        author_club_id="arsenal",
        club_id="arsenal",
        content="Declan Rice's ball-carrying and ground duel winning rate (68.4%) make him indispensable in European ties. Look at the central stability he brings to our spine. #DataLab #Arsenal #COYG",
        image_url="https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=800&q=80",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
        reactions_count=34,
        comments_count=6,
        user_reacted=False,
    ),
    PostResponse(
        id="post_seed_3",
        author_id="usr_seed_clock",
        author_name="ClockEndTactician",
        author_club_id="arsenal",
        club_id="arsenal",
        content="When teams sit in a disciplined 5-3-2 low block, Arteta's solution is to invert Timber into the midfield pocket, allowing Merino to crash the box as an extra aerial threat. #Tactics #Emirates",
        tactical_board_id="tb_arsenal_highpress",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6),
        reactions_count=22,
        comments_count=3,
        user_reacted=False,
    ),
    PostResponse(
        id="post_seed_4",
        author_id="usr_seed_nb",
        author_name="NorthBankFan",
        author_club_id="arsenal",
        club_id="arsenal",
        content="The atmosphere under the floodlights this week was electric. Big three points secured! Proud to be a Gooner. #Arsenal #PremierLeague #Gunners",
        image_url="https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=800&q=80",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=8),
        reactions_count=41,
        comments_count=5,
        user_reacted=False,
    ),
]


def serialize_tactical_board_response(tb: Optional[TacticalBoard]) -> Optional[TacticalBoardResponse]:
    if not tb:
        return None
    return TacticalBoardResponse(
        id=tb.id,
        user_id=tb.user_id,
        author_name=tb.author_name,
        author_club_id=tb.author_club_id,
        title=tb.title,
        formation=tb.formation,
        lineup=tb.lineup,
        annotations=tb.annotations or [],
        tactical_notes=tb.tactical_notes,
        is_public=tb.is_public,
        created_at=tb.created_at,
        updated_at=tb.updated_at,
    )


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
        created_at=ins.created_at,
    )


@router.get("/posts", response_model=List[PostResponse])
async def list_posts(
    optional_user: OptionalUserDep,
    club_id: Optional[str] = Query(None, description="Filter by club or 'global'"),
    search: Optional[str] = Query(None, description="Search post content or author name"),
    tag: Optional[str] = Query(None, description="Filter by topic hashtag (e.g. #NorthLondonDerby)"),
    current_user_id: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List terrace community posts with search, hashtag filter, reaction counts, and attached insights."""
    effective_user_id = optional_user.id if optional_user else current_user_id

    stmt = (
        select(Post)
        .options(
            selectinload(Post.insight),
            selectinload(Post.tactical_board),
            selectinload(Post.comments),
            selectinload(Post.reactions),
        )
        .order_by(desc(Post.created_at))
    )

    if club_id and club_id not in ("global", "all"):
        stmt = stmt.where(Post.club_id == club_id)

    if search:
        search_pattern = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Post.content).like(search_pattern),
                func.lower(Post.author_name).like(search_pattern),
            )
        )

    if tag:
        tag_pattern = f"%{tag.strip().lower()}%"
        stmt = stmt.where(func.lower(Post.content).like(tag_pattern))

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    posts = res.scalars().all()

    result: List[PostResponse] = []
    for p in posts:
        reactions_cnt = len(p.reactions)
        comments_cnt = len(p.comments)
        user_reacted = (
            any(r.user_id == effective_user_id for r in p.reactions)
            if effective_user_id
            else False
        )

        result.append(
            PostResponse(
                id=p.id,
                author_id=p.author_id,
                author_name=p.author_name,
                author_club_id=p.author_club_id,
                club_id=p.club_id,
                content=p.content,
                image_url=p.image_url,
                insight_id=p.insight_id,
                insight=serialize_insight_response(p.insight),
                tactical_board_id=p.tactical_board_id,
                tactical_board=serialize_tactical_board_response(p.tactical_board),
                created_at=p.created_at,
                reactions_count=reactions_cnt,
                comments_count=comments_cnt,
                user_reacted=user_reacted,
            )
        )

    if not result and not search and not tag:
        total_in_db = (await db.execute(select(func.count(Post.id)))).scalar() or 0
        if total_in_db == 0:
            fallback_posts = list(DEFAULT_POSTS)
            if club_id and club_id not in ("global", "all"):
                fallback_posts = [
                    p
                    for p in fallback_posts
                    if p.club_id == club_id or p.author_club_id == club_id
                ]
            return fallback_posts[:limit]

    return result


@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    request: PostCreateRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Publish a post to The Terrace with optional insight or tactical board attachment."""
    attached_insight = None
    if request.insight_id:
        ins_res = await db.execute(select(Insight).where(Insight.id == request.insight_id))
        attached_insight = ins_res.scalar_one_or_none()
        if not attached_insight:
            raise HTTPException(status_code=400, detail="Attached insight not found")

    attached_board = None
    if request.tactical_board_id:
        tb_res = await db.execute(
            select(TacticalBoard).where(TacticalBoard.id == request.tactical_board_id)
        )
        attached_board = tb_res.scalar_one_or_none()
        if not attached_board:
            raise HTTPException(status_code=400, detail="Attached tactical board not found")

    author_name = (
        current_user.display_name
        if not request.author_name or request.author_name == "Supporter"
        else request.author_name
    )
    author_club_id = request.author_club_id or current_user.club_id or "arsenal"
    post_club_id = request.club_id if request.club_id not in (None, "global") else None

    post_id = f"post_{uuid.uuid4().hex[:12]}"
    new_post = Post(
        id=post_id,
        author_id=current_user.id,
        author_name=author_name,
        author_club_id=author_club_id,
        club_id=post_club_id,
        content=request.content,
        image_url=request.image_url,
        insight_id=request.insight_id,
        tactical_board_id=request.tactical_board_id,
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
        image_url=new_post.image_url,
        insight_id=new_post.insight_id,
        insight=serialize_insight_response(attached_insight),
        tactical_board_id=new_post.tactical_board_id,
        tactical_board=serialize_tactical_board_response(attached_board),
        created_at=new_post.created_at,
        reactions_count=0,
        comments_count=0,
        user_reacted=False,
    )


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Delete a Terrace post owned by the authenticated user."""
    post_res = await db.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.author_id or post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    # Clean up child rows explicitly so SQLite tests (with PRAGMA foreign_keys off) stay consistent.
    await db.execute(delete(PostComment).where(PostComment.post_id == post_id))
    await db.execute(delete(PostReaction).where(PostReaction.post_id == post_id))
    await db.execute(delete(Post).where(Post.id == post_id))
    await db.commit()
    return {"status": "deleted", "id": post_id}


async def _toggle_post_reaction(
    post_id: str,
    request: ReactionToggleRequest,
    current_user: CurrentUserDep,
    db: AsyncSession,
):
    post_res = await db.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_stmt = select(PostReaction).where(
        and_(
            PostReaction.post_id == post_id,
            PostReaction.user_id == current_user.id,
            PostReaction.reaction_type == request.reaction_type,
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
            user_id=current_user.id,
            reaction_type=request.reaction_type,
        )
        db.add(new_reaction)
        action = "added"
        if post.author_id and post.author_id != current_user.id:
            await create_notification(
                db,
                user_id=post.author_id,
                notif_type="cheer",
                title="Matchday Cheer",
                message=f"{current_user.display_name} cheered your Terrace post.",
                link=f"/terrace#post-{post.id}",
            )

    await db.commit()

    count_stmt = select(func.count(PostReaction.id)).where(PostReaction.post_id == post_id)
    total_count = (await db.execute(count_stmt)).scalar() or 0

    return {
        "action": action,
        "reaction_type": request.reaction_type,
        "total_reactions": total_count,
    }


@router.post("/posts/{post_id}/react")
async def toggle_reaction(
    post_id: str,
    request: ReactionToggleRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Toggle a reaction on a post for the authenticated user."""
    return await _toggle_post_reaction(post_id, request, current_user, db)


@router.post("/posts/{post_id}/cheer")
async def toggle_cheer(
    post_id: str,
    current_user: CurrentUserDep,
    request: Optional[ReactionToggleRequest] = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a cheer reaction on a post for the authenticated user."""
    payload = request if request is not None else ReactionToggleRequest(reaction_type="cheer")
    return await _toggle_post_reaction(post_id, payload, current_user, db)


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    post_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List comments under a post."""
    stmt = (
        select(PostComment)
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: str,
    request: CommentCreateRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Add a comment under a post."""
    post_res = await db.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    author_name = (
        current_user.display_name
        if not request.author_name or request.author_name == "Supporter"
        else request.author_name
    )
    author_club_id = request.author_club_id or current_user.club_id or "arsenal"

    comment_id = f"cmt_{uuid.uuid4().hex[:10]}"
    new_comment = PostComment(
        id=comment_id,
        post_id=post_id,
        author_id=current_user.id,
        author_name=author_name,
        author_club_id=author_club_id,
        content=request.content,
    )

    db.add(new_comment)
    if post.author_id and post.author_id != current_user.id:
        clean_text = " ".join(request.content.split())
        snippet = (clean_text[:100] + "...") if len(clean_text) > 103 else clean_text
        await create_notification(
            db,
            user_id=post.author_id,
            notif_type="reply",
            title="New Terrace Reply",
            message=f"{author_name} replied: {snippet}",
            link=f"/terrace#post-{post.id}",
        )

    await db.commit()
    await db.refresh(new_comment)
    return new_comment


@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(
    post_id: str,
    comment_id: str,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment owned by the authenticated user."""
    stmt = select(PostComment).where(
        and_(PostComment.id == comment_id, PostComment.post_id == post_id)
    )
    comment = (await db.execute(stmt)).scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not comment.author_id or comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await db.execute(delete(PostComment).where(PostComment.id == comment_id))
    await db.commit()
    return {"status": "deleted", "id": comment_id}


@router.get("/tags")
async def list_trending_tags(db: AsyncSession = Depends(get_db)):
    """Compute trending #hashtag counts dynamically from Post.content rows in DB."""
    stmt = select(Post.content, Post.club_id, Post.author_club_id)
    rows = (await db.execute(stmt)).all()
    if not rows:
        return []

    tag_counts: Counter[str] = Counter()
    tag_casings: dict[str, Counter[str]] = {}
    tag_clubs: dict[str, Counter[str]] = {}

    for content, club_id, author_club_id in rows:
        if not content:
            continue
        seen_in_post: set[str] = set()
        effective_club = club_id or author_club_id or "arsenal"
        for match in _HASHTAG_RE.finditer(content):
            raw_tag = match.group(1)
            key = raw_tag.lower()
            if key in seen_in_post:
                continue
            seen_in_post.add(key)
            tag_counts[key] += 1
            tag_casings.setdefault(key, Counter())[raw_tag] += 1
            tag_clubs.setdefault(key, Counter())[effective_club] += 1

    if not tag_counts:
        return []

    trending = []
    for key, count in tag_counts.most_common(10):
        canonical_tag = tag_casings[key].most_common(1)[0][0]
        top_club = tag_clubs[key].most_common(1)[0][0]
        trending.append(
            {
                "tag": canonical_tag,
                "count": count,
                "club": top_club if top_club == "arsenal" else "global",
            }
        )
    return trending
