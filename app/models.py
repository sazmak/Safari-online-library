from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db




CATEGORIES = [
    ('video', 'Видеоуроки'),
    ('book', 'Книги/Учебники'),
    ('article', 'Статьи'),
    ('project', 'Проекты'),
    ('other', 'Прочее')
]
    

# ─── User ────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash   = db.Column(db.String(256), nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(200), nullable=True)

    # Relationships
    resources = db.relationship("Resource", back_populates="author",
                                lazy="dynamic", cascade="all, delete-orphan")
    comments  = db.relationship("Comment",  back_populates="author",
                                lazy="dynamic", cascade="all, delete-orphan")
    votes     = db.relationship("UserVote", back_populates="user",
                                lazy="dynamic", cascade="all, delete-orphan")

    # ── helpers ──────────────────────────────────────────────────────────────
    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    @property
    def resource_count(self) -> int:
        return self.resources.count()

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# ─── Resource ────────────────────────────────────────────────────────────────

class Resource(db.Model):
    __tablename__ = "resources"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    link        = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    subject     = db.Column(db.String(100))
    category    = db.Column(db.String(50), nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ── new vote counters ─────────────────────────────────────────────────────
    likes    = db.Column(db.Integer, default=0, nullable=False)
    dislikes = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    author   = db.relationship("User",    back_populates="resources")
    comments = db.relationship("Comment", back_populates="resource",
                               lazy="dynamic", order_by="Comment.timestamp.asc()",
                               cascade="all, delete-orphan")
    votes    = db.relationship("UserVote", back_populates="resource",
                               lazy="dynamic", cascade="all, delete-orphan")

    # ── helpers ──────────────────────────────────────────────────────────────
    @property
    def short_description(self) -> str | None:
        if self.description:
            return self.description[:140] + ("…" if len(self.description) > 140 else "")
        return None

    def user_vote(self, user_id: int) -> str | None:
        """Return 'like', 'dislike', or None for the given user."""
        v = UserVote.query.filter_by(resource_id=self.id, user_id=user_id).first()
        return v.value if v else None

    def __repr__(self) -> str:
        return f"<Resource {self.title[:40]}>"


# ─── Comment ─────────────────────────────────────────────────────────────────

class Comment(db.Model):
    __tablename__ = "comments"

    id          = db.Column(db.Integer, primary_key=True)
    text        = db.Column(db.Text, nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),     nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)

    # Relationships
    author   = db.relationship("User",     back_populates="comments")
    resource = db.relationship("Resource", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment {self.id} by {self.user_id}>"


# ─── UserVote ────────────────────────────────────────────────────────────────
# Tracks per-user votes so users cannot vote twice on the same resource.

class UserVote(db.Model):
    __tablename__ = "user_votes"
    __table_args__ = (
        db.UniqueConstraint("user_id", "resource_id", name="uq_user_resource_vote"),
    )

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),     nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    # value is either 'like' or 'dislike'
    value       = db.Column(db.String(10), nullable=False)

    # Relationships
    user     = db.relationship("User",     back_populates="votes")
    resource = db.relationship("Resource", back_populates="votes")

    def __repr__(self) -> str:
        return f"<UserVote {self.value} u={self.user_id} r={self.resource_id}>"