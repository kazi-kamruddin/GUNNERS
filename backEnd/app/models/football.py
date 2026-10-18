import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
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
    crest_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_foundation: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)  # e.g. PL, PD, SA, CL
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    emblem_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. 2024-2025-PL
    competition_id: Mapped[str] = mapped_column(String(50), nullable=False)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    competition_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    competition_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    season_id: Mapped[str] = mapped_column(String(50), nullable=False)
    home_team_id: Mapped[str] = mapped_column(String(50), nullable=False)
    home_team_name: Mapped[str] = mapped_column(String(100), default="Home Team")
    home_team_crest: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    away_team_id: Mapped[str] = mapped_column(String(50), nullable=False)
    away_team_name: Mapped[str] = mapped_column(String(100), default="Away Team")
    away_team_crest: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    matchday: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    utc_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED")  # FINISHED, SCHEDULED, IN_PLAY, POSTPONED
    venue: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Final Result
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    winner: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # HOME_TEAM, AWAY_TEAM, DRAW

    source: Mapped[str] = mapped_column(String(50), default="football-data.org")
    last_updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("idx_matches_teams", "home_team_id", "away_team_id"),
        Index("idx_matches_status_date", "status", "utc_date"),
    )

class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), default="football-data.org")
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS")
    matches_synced: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
