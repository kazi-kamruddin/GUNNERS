import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_color: Mapped[str] = mapped_column(String(20), nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(20), nullable=False)
    accent_color: Mapped[str] = mapped_column(String(20), nullable=False)
    league: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)  # e.g. PL, PD, SA
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. 2024-2025
    competition_id: Mapped[str] = mapped_column(String(50), ForeignKey("competitions.id"), nullable=False)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    competition_id: Mapped[str] = mapped_column(String(50), ForeignKey("competitions.id"), nullable=False)
    season_id: Mapped[str] = mapped_column(String(50), ForeignKey("seasons.id"), nullable=False)
    home_team_id: Mapped[str] = mapped_column(String(50), ForeignKey("clubs.id"), nullable=False)
    away_team_id: Mapped[str] = mapped_column(String(50), ForeignKey("clubs.id"), nullable=False)
    
    matchday: Mapped[int] = mapped_column(Integer, nullable=True)
    utc_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED")  # FINISHED, SCHEDULED, IN_PLAY, POSTPONED
    venue: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Final Result
    home_score: Mapped[int] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int] = mapped_column(Integer, nullable=True)
    winner: Mapped[str] = mapped_column(String(20), nullable=True)  # HOME_TEAM, AWAY_TEAM, DRAW

    source: Mapped[str] = mapped_column(String(50), default="football-data.org")
    last_updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("idx_matches_teams", "home_team_id", "away_team_id"),
        Index("idx_matches_status_date", "status", "utc_date"),
    )
