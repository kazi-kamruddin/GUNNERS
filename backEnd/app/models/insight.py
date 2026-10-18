import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    author_name: Mapped[str] = mapped_column(String(100), default="Supporter")
    author_club_id: Mapped[str] = mapped_column(String(50), default="arsenal")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    team_ids: Mapped[str] = mapped_column(String(100), nullable=False)  # Comma-separated canonical club ids
    venue: Mapped[str] = mapped_column(String(20), default="all")
    competition_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    chart_type: Mapped[str] = mapped_column(String(50), default="bar")
    snapshot: Mapped[str] = mapped_column(Text, nullable=False)  # Serialized JSON snapshot
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)
