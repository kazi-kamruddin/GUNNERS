from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class MessageCreateRequest(BaseModel):
    sender_id: str = Field(..., max_length=100)
    sender_name: str = Field("Supporter", max_length=100)
    sender_club_id: str = Field("arsenal", max_length=50)
    content: str = Field(..., min_length=1, max_length=2000)

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    sender_name: str
    sender_club_id: str
    content: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class ConversationCreateRequest(BaseModel):
    initiator_id: str = Field(..., max_length=100)
    recipient_id: str = Field(..., max_length=100)
    initiator_name: str = Field("Supporter", max_length=100)
    initiator_club_id: str = Field("arsenal", max_length=50)
    initial_message: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    members: List[str]
    last_message: Optional[MessageResponse] = None

    model_config = {"from_attributes": True}
