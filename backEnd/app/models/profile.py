import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    # Intentionally omit cross-schema ForeignKey("auth.users.id") so Base.metadata.create_all
    # works cleanly on SQLite :memory: tests while still mapping public.profiles in Postgres.
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    favorite_club_id: Mapped[str] = mapped_column(String(50), default="arsenal", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    __table_args__ = (
        Index("idx_profiles_favorite_club", "favorite_club_id"),
    )
