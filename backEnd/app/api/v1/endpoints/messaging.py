import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.models.messaging import Conversation, ConversationMember, DirectMessage
from app.schemas.messaging import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse
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
        created_at=msg.created_at
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = Query(..., description="User ID to list conversations for"),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations for a given user, including members and last message."""
    subq = select(ConversationMember.conversation_id).where(ConversationMember.user_id == user_id)
    stmt = (
        select(Conversation)
        .where(Conversation.id.in_(subq))
        .options(
            selectinload(Conversation.members),
            selectinload(Conversation.messages)
        )
        .order_by(desc(Conversation.updated_at))
    )
    res = await db.execute(stmt)
    conversations = res.scalars().all()

    result = []
    for c in conversations:
        member_ids = [m.user_id for m in c.members]
        last_msg = c.messages[-1] if c.messages else None
        result.append(
            ConversationResponse(
                id=c.id,
                created_at=c.created_at,
                updated_at=c.updated_at,
                members=member_ids,
                last_message=serialize_message(last_msg)
            )
        )
    return result

@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a new direct messaging debate or return existing conversation between two users."""
    if request.initiator_id == request.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot start conversation with yourself")

    # Check for existing conversation with both users
    member_convs_1 = select(ConversationMember.conversation_id).where(ConversationMember.user_id == request.initiator_id)
    member_convs_2 = select(ConversationMember.conversation_id).where(ConversationMember.user_id == request.recipient_id)
    common_stmt = (
        select(Conversation)
        .where(
            and_(
                Conversation.id.in_(member_convs_1),
                Conversation.id.in_(member_convs_2)
            )
        )
        .options(
            selectinload(Conversation.members),
            selectinload(Conversation.messages)
        )
    )
    common_res = await db.execute(common_stmt)
    existing = common_res.scalars().first()

    now = datetime.datetime.utcnow()

    if existing:
        last_msg = existing.messages[-1] if existing.messages else None
        if request.initial_message:
            msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            new_msg = DirectMessage(
                id=msg_id,
                conversation_id=existing.id,
                sender_id=request.initiator_id,
                sender_name=request.initiator_name,
                sender_club_id=request.initiator_club_id,
                content=request.initial_message,
                created_at=now
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
            last_message=serialize_message(last_msg)
        )

    # Create new conversation
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    conv = Conversation(
        id=conv_id,
        created_at=now,
        updated_at=now
    )
    db.add(conv)

    # Add members
    m1 = ConversationMember(conversation_id=conv_id, user_id=request.initiator_id, joined_at=now, last_read_at=now)
    m2 = ConversationMember(conversation_id=conv_id, user_id=request.recipient_id, joined_at=now, last_read_at=now)
    db.add_all([m1, m2])

    last_msg = None
    if request.initial_message:
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        last_msg = DirectMessage(
            id=msg_id,
            conversation_id=conv_id,
            sender_id=request.initiator_id,
            sender_name=request.initiator_name,
            sender_club_id=request.initiator_club_id,
            content=request.initial_message,
            created_at=now
        )
        db.add(last_msg)

    await db.commit()

    return ConversationResponse(
        id=conv_id,
        created_at=now,
        updated_at=now,
        members=[request.initiator_id, request.recipient_id],
        last_message=serialize_message(last_msg)
    )

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Fetch messages in chronological order for a conversation."""
    stmt = (
        select(DirectMessage)
        .where(DirectMessage.conversation_id == conversation_id)
        .order_by(DirectMessage.created_at.asc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    conversation_id: str,
    request: MessageCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a direct message within a conversation."""
    conv_res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = conv_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    now = datetime.datetime.utcnow()
    new_msg = DirectMessage(
        id=msg_id,
        conversation_id=conversation_id,
        sender_id=request.sender_id,
        sender_name=request.sender_name,
        sender_club_id=request.sender_club_id,
        content=request.content,
        created_at=now
    )
    conv.updated_at = now
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg
