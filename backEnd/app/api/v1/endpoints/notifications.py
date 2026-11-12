from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, update
from app.core.database import get_db
from app.core.security import CurrentUserDep
from app.models.notifications import Notification
from app.schemas.notifications import NotificationResponse, UnreadCountResponse

router = APIRouter()


def _verify_user_scope(requested_user_id: Optional[str], current_user_id: str) -> None:
    if requested_user_id is not None and requested_user_id != current_user_id:
        raise HTTPException(
            status_code=403, detail="Cannot access notifications for another user"
        )


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    current_user: CurrentUserDep,
    user_id: Optional[str] = Query(None, description="Optional user ID check; must match current user"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve notifications for the authenticated user."""
    _verify_user_scope(user_id, current_user.id)

    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(desc(Notification.created_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: CurrentUserDep,
    user_id: Optional[str] = Query(None, description="Optional user ID check; must match current user"),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications for the authenticated user."""
    _verify_user_scope(user_id, current_user.id)

    stmt = select(func.count(Notification.id)).where(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    cnt = (await db.execute(stmt)).scalar() or 0
    return UnreadCountResponse(unread_count=int(cnt))


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification belonging to the authenticated user as read."""
    stmt = select(Notification).where(Notification.id == notification_id)
    notif = (await db.execute(stmt)).scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this notification")

    notif.is_read = True
    await db.commit()
    return {"status": "success", "id": notification_id}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: CurrentUserDep,
    user_id: Optional[str] = Query(None, description="Optional user ID check; must match current user"),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read for the authenticated user."""
    _verify_user_scope(user_id, current_user.id)

    stmt = (
        update(Notification)
        .where(Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()
    return {"status": "success", "user_id": current_user.id}
