import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), default="Supporter")
    user_club_id: Mapped[str] = mapped_column(String(50), default="arsenal")
    match_id: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    points_awarded: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "match_id", name="uq_user_match_prediction"),
        Index("idx_predictions_user", "user_id"),
        Index("idx_predictions_match", "match_id"),
    )
