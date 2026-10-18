from pydantic import BaseModel
import datetime

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    link: str
    is_read: bool
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class UnreadCountResponse(BaseModel):
    unread_count: int
