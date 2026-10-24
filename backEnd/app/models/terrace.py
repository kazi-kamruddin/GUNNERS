import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.insight import Insight
from app.models.tactics import TacticalBoard

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    author_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    author_name: Mapped[str] = mapped_column(String(100), default="Supporter")
    author_club_id: Mapped[str] = mapped_column(String(50), default="arsenal")
    club_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # NULL or specific club
    content: Mapped[str] = mapped_column(Text, nullable=False)
    insight_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("insights.id", ondelete="SET NULL"), nullable=True)
    tactical_board_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("tactical_boards.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    insight: Mapped[Optional[Insight]] = relationship("Insight", lazy="joined")
    tactical_board: Mapped[Optional[TacticalBoard]] = relationship("TacticalBoard", lazy="joined")
    comments: Mapped[List["PostComment"]] = relationship("PostComment", back_populates="post", cascade="all, delete-orphan", order_by="PostComment.created_at.asc()")
    reactions: Mapped[List["PostReaction"]] = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_posts_created_at", "created_at"),
        Index("idx_posts_club_id", "club_id"),
    )

class PostComment(Base):
    __tablename__ = "post_comments"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    post_id: Mapped[str] = mapped_column(String(50), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    author_name: Mapped[str] = mapped_column(String(100), default="Supporter")
    author_club_id: Mapped[str] = mapped_column(String(50), default="arsenal")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    post: Mapped[Post] = relationship("Post", back_populates="comments")

    __table_args__ = (
        Index("idx_post_comments_post_id", "post_id", "created_at"),
    )

class PostReaction(Base):
    __tablename__ = "post_reactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    post_id: Mapped[str] = mapped_column(String(50), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    reaction_type: Mapped[str] = mapped_column(String(20), default="cheer")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    post: Mapped[Post] = relationship("Post", back_populates="reactions")

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", "reaction_type", name="uq_post_user_reaction"),
        Index("idx_post_reactions_post_id", "post_id"),
    )
