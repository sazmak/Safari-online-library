from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime, ForeignKey, Index, Integer, String, Text,
    UniqueConstraint, func, select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


# ─── User ────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id:              Mapped[int]           = mapped_column(primary_key=True)
    username:        Mapped[str]           = mapped_column(String(120), unique=True, nullable=False)
    email:           Mapped[Optional[str]] = mapped_column(String(200), unique=True, nullable=True, index=True)
    password_hash:   Mapped[str]           = mapped_column(String(256), nullable=False)
    created_at:      Mapped[datetime]      = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    profile_picture: Mapped[Optional[str]] = mapped_column(String(200))

    resources: Mapped[list[Resource]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    votes: Mapped[list[UserVote]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    @property
    def resource_count(self) -> int:
        return len(self.resources)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# ─── Resource ────────────────────────────────────────────────────────────────

class Resource(db.Model):
    __tablename__ = "resources"
    __table_args__ = (
        Index("ix_resources_user_id",  "user_id"),
        Index("ix_resources_category", "category"),
    )

    id:          Mapped[int]           = mapped_column(primary_key=True)
    title:       Mapped[str]           = mapped_column(String(200), nullable=False)
    link:        Mapped[str]           = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    subject:     Mapped[Optional[str]] = mapped_column(String(100))
    category:    Mapped[str]           = mapped_column(String(50), nullable=False)
    timestamp:   Mapped[datetime]      = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )
    user_id:  Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    likes:    Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dislikes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    author:   Mapped[User]          = relationship(back_populates="resources")
    comments: Mapped[list[Comment]] = relationship(
        back_populates="resource",
        cascade="all, delete-orphan",
        order_by="Comment.timestamp",
    )
    votes: Mapped[list[UserVote]] = relationship(
        back_populates="resource", cascade="all, delete-orphan"
    )

    @property
    def short_description(self) -> str | None:
        if self.description:
            return self.description[:140] + ("…" if len(self.description) > 140 else "")
        return None

    def user_vote(self, user_id: int) -> str | None:
        v = db.session.execute(
            select(UserVote).filter_by(resource_id=self.id, user_id=user_id)
        ).scalar_one_or_none()
        return v.value if v else None

    def __repr__(self) -> str:
        return f"<Resource {self.title[:40]}>"


# ─── Comment ─────────────────────────────────────────────────────────────────

class Comment(db.Model):
    __tablename__ = "comments"
    __table_args__ = (
        Index("ix_comments_resource_id", "resource_id"),
        Index("ix_comments_user_id",     "user_id"),
    )

    id:          Mapped[int]      = mapped_column(primary_key=True)
    text:        Mapped[str]      = mapped_column(Text, nullable=False)
    timestamp:   Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )
    user_id:     Mapped[int] = mapped_column(ForeignKey("users.id"),     nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), nullable=False)

    author:   Mapped[User]     = relationship(back_populates="comments")
    resource: Mapped[Resource] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment {self.id} by user={self.user_id}>"


# ─── UserVote ────────────────────────────────────────────────────────────────

class UserVote(db.Model):
    __tablename__ = "user_votes"
    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource_vote"),
        Index("ix_uservote_resource_id", "resource_id"),
        Index("ix_uservote_user_id",     "user_id"),
    )

    id:          Mapped[int] = mapped_column(primary_key=True)
    user_id:     Mapped[int] = mapped_column(ForeignKey("users.id"),     nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), nullable=False)
    value:       Mapped[str] = mapped_column(String(10), nullable=False)

    user:     Mapped[User]     = relationship(back_populates="votes")
    resource: Mapped[Resource] = relationship(back_populates="votes")

    def __repr__(self) -> str:
        return f"<UserVote {self.value} u={self.user_id} r={self.resource_id}>"
