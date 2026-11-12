import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import CurrentUserDep
from app.models.messaging import Conversation, ConversationMember, DirectMessage
from app.models.profile import Profile
from app.schemas.messaging import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)

router = APIRouter()


def serialize_message(msg: Optional[DirectMessage]) -> Optional[MessageResponse]:
    if not msg:
        return None
    return MessageResponse(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender_id=msg.sender_id,
        sender_name=msg.sender_name,
        sender_club_id=msg.sender_club_id,
        content=msg.content,
        created_at=msg.created_at,
    )


async def _ensure_conversation_member(
    db: AsyncSession, conversation_id: str, user_id: str
) -> Conversation:
    conv_res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = conv_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    member_res = await db.execute(
        select(ConversationMember).where(
            and_(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == user_id,
            )
        )
    )
    if not member_res.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this conversation")
    return conv


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: CurrentUserDep,
    user_id: Optional[str] = Query(None, description="Optional user ID check; must match current user"),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the authenticated user, including members and last message."""
    if user_id is not None and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access conversations for another user")

    subq = select(ConversationMember.conversation_id).where(
        ConversationMember.user_id == current_user.id
    )
    stmt = (
        select(Conversation)
        .where(Conversation.id.in_(subq))
        .options(
            selectinload(Conversation.members),
            selectinload(Conversation.messages),
        )
        .order_by(desc(Conversation.updated_at))
    )
    res = await db.execute(stmt)
    conversations = res.scalars().all()

    result: List[ConversationResponse] = []
    for c in conversations:
        member_ids = [m.user_id for m in c.members]
        last_msg = c.messages[-1] if c.messages else None
        result.append(
            ConversationResponse(
                id=c.id,
                created_at=c.created_at,
                updated_at=c.updated_at,
                members=member_ids,
                last_message=serialize_message(last_msg),
            )
        )
    return result


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Start a new direct messaging debate or return existing conversation between two users."""
    initiator_id = current_user.id
    if request.recipient_id == initiator_id:
        raise HTTPException(status_code=400, detail="Cannot start conversation with yourself")

    # Optionally enrich initiator name from Profile if available
    profile_res = await db.execute(select(Profile).where(Profile.id == initiator_id))
    initiator_profile = profile_res.scalar_one_or_none()
    initiator_name = (
        (initiator_profile.display_name or initiator_profile.username)
        if initiator_profile
        else None
    )
    if not initiator_name:
        initiator_name = (
            current_user.display_name
            if not request.initiator_name or request.initiator_name == "Supporter"
            else request.initiator_name
        )
    initiator_club_id = (
        request.initiator_club_id
        or (initiator_profile.favorite_club_id if initiator_profile else None)
        or current_user.club_id
        or "arsenal"
    )

    member_convs_1 = select(ConversationMember.conversation_id).where(
        ConversationMember.user_id == initiator_id
    )
    member_convs_2 = select(ConversationMember.conversation_id).where(
        ConversationMember.user_id == request.recipient_id
    )
    common_stmt = (
        select(Conversation)
        .where(
            and_(
                Conversation.id.in_(member_convs_1),
                Conversation.id.in_(member_convs_2),
            )
        )
        .options(
            selectinload(Conversation.members),
            selectinload(Conversation.messages),
        )
    )
    existing = (await db.execute(common_stmt)).scalars().first()

    now = datetime.datetime.now(datetime.timezone.utc)

    if existing:
        last_msg = existing.messages[-1] if existing.messages else None
        if request.initial_message:
            msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            new_msg = DirectMessage(
                id=msg_id,
                conversation_id=existing.id,
                sender_id=initiator_id,
                sender_name=initiator_name,
                sender_club_id=initiator_club_id,
                content=request.initial_message,
                created_at=now,
            )
            existing.updated_at = now
            db.add(new_msg)
            await db.commit()
            last_msg = new_msg

        return ConversationResponse(
            id=existing.id,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
            members=[m.user_id for m in existing.members],
            last_message=serialize_message(last_msg),
        )

    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    conv = Conversation(
        id=conv_id,
        created_at=now,
        updated_at=now,
    )
    db.add(conv)

    m1 = ConversationMember(
        conversation_id=conv_id, user_id=initiator_id, joined_at=now, last_read_at=now
    )
    m2 = ConversationMember(
        conversation_id=conv_id, user_id=request.recipient_id, joined_at=now, last_read_at=now
    )
    db.add_all([m1, m2])

    last_msg = None
    if request.initial_message:
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        last_msg = DirectMessage(
            id=msg_id,
            conversation_id=conv_id,
            sender_id=initiator_id,
            sender_name=initiator_name,
            sender_club_id=initiator_club_id,
            content=request.initial_message,
            created_at=now,
        )
        db.add(last_msg)

    await db.commit()

    return ConversationResponse(
        id=conv_id,
        created_at=now,
        updated_at=now,
        members=[initiator_id, request.recipient_id],
        last_message=serialize_message(last_msg),
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: CurrentUserDep,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Fetch messages in chronological order for a conversation the user belongs to."""
    await _ensure_conversation_member(db, conversation_id, current_user.id)

    stmt = (
        select(DirectMessage)
        .where(DirectMessage.conversation_id == conversation_id)
        .order_by(DirectMessage.created_at.asc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post(
    "/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=201
)
async def send_message(
    conversation_id: str,
    request: MessageCreateRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Send a direct message within a conversation the user belongs to."""
    conv = await _ensure_conversation_member(db, conversation_id, current_user.id)

    sender_name = (
        current_user.display_name
        if not request.sender_name or request.sender_name == "Supporter"
        else request.sender_name
    )
    sender_club_id = request.sender_club_id or current_user.club_id or "arsenal"

    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    now = datetime.datetime.now(datetime.timezone.utc)
    new_msg = DirectMessage(
        id=msg_id,
        conversation_id=conversation_id,
        sender_id=current_user.id,
        sender_name=sender_name,
        sender_club_id=sender_club_id,
        content=request.content,
        created_at=now,
    )
    conv.updated_at = now
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg
