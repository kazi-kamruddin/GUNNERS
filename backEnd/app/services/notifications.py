import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import Notification


async def create_notification(
    db: AsyncSession,
    *,
    user_id: str,
    notif_type: str,
    title: str,
    message: str,
    link: str = "/",
) -> Notification:
    """Create and stage an in-app Notification row without committing the caller's transaction."""
    notif = Notification(
        id=f"notif_{uuid.uuid4().hex[:12]}",
        user_id=user_id[:100],
        type=notif_type[:30],
        title=title[:150],
        message=message[:255],
        link=(link or "/")[:255],
        is_read=False,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(notif)
    return notif
