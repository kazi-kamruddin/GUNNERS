import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    club_id: Mapped[str] = mapped_column(String(50), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[str] = mapped_column(String(30), nullable=False)  # Goalkeeper, Defender, Midfielder, Attacker
    jersey_number: Mapped[int] = mapped_column(Integer, nullable=False)
    nationality: Mapped[str] = mapped_column(String(50), nullable=False)
    appearances: Mapped[int] = mapped_column(Integer, default=0)
    goals: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    clean_sheets: Mapped[int] = mapped_column(Integer, default=0)
    minutes_played: Mapped[int] = mapped_column(Integer, default=0)
    yellow_cards: Mapped[int] = mapped_column(Integer, default=0)
    red_cards: Mapped[int] = mapped_column(Integer, default=0)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    club = relationship("Club", backref="players")

    __table_args__ = (
        Index("idx_players_club", "club_id"),
        Index("idx_players_position", "position"),
    )
