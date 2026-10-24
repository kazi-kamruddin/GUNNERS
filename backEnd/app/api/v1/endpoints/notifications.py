import uuid
import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, update
from typing import List, Optional
from app.core.database import get_db
from app.models.notifications import Notification
from app.schemas.notifications import NotificationResponse, UnreadCountResponse

router = APIRouter()

DEFAULT_NOTIFICATIONS = [
    {
        "id": "notif_welcome",
        "type": "welcome",
        "title": "Welcome to GUNNERS Reborn!",
        "message": "Explore verified metrics in the Data Lab and debate supporters on The Terrace.",
        "link": "/lab",
        "is_read": False,
        "created_at": datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    },
    {
        "id": "notif_insight_pub",
        "type": "cheer",
        "title": "Trending Insight",
        "message": "Your Arsenal Home Win Rate analysis was featured on the Community Evidence shelf.",
        "link": "/terrace",
        "is_read": False,
        "created_at": datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    }
]

@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve notifications for a user."""
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(desc(Notification.created_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    items = res.scalars().all()

    if items:
        return items

    # Return baseline welcome notifications
    return [
        NotificationResponse(
            id=f"{n['id']}_{user_id[:6]}",
            user_id=user_id,
            type=n["type"],
            title=n["title"],
            message=n["message"],
            link=n["link"],
            is_read=n["is_read"],
            created_at=n["created_at"]
        )
        for n in DEFAULT_NOTIFICATIONS
    ]

@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications for a user."""
    stmt = (
        select(func.count(Notification.id))
        .where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
    )
    cnt = (await db.execute(stmt)).scalar() or 0

    # If user has no notifications in DB yet, fallback count is 2 (from defaults)
    if cnt == 0:
        total_stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        total = (await db.execute(total_stmt)).scalar() or 0
        if total == 0:
            cnt = 2

    return UnreadCountResponse(unread_count=cnt)

@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read."""
    stmt = select(Notification).where(Notification.id == notification_id)
    notif = (await db.execute(stmt)).scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.commit()
    return {"status": "success", "id": notification_id}

@router.post("/read-all")
async def mark_all_as_read(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read for a user."""
    stmt = update(Notification).where(Notification.user_id == user_id).values(is_read=True)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success", "user_id": user_id}
