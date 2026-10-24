import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Boolean, DateTime, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TacticalBoard(Base):
    __tablename__ = "tactical_boards"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    author_name: Mapped[str] = mapped_column(String(100), default="Supporter")
    author_club_id: Mapped[str] = mapped_column(String(50), default="arsenal")
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    formation: Mapped[str] = mapped_column(String(20), default="4-3-3")
    lineup: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    annotations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    tactical_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("idx_tactical_boards_club", "author_club_id"),
        Index("idx_tactical_boards_created", "created_at"),
    )
