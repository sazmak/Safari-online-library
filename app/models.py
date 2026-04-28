from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 

CATEGORIES = [
    ('lecture', 'Лекция'),
    ('book',    'Учебник'),
    ('article', 'Статья'),
    ('video',   'Видео'),
    ('task',    'Задание'),
    ('other',   'Другое'),
]

CATEGORY_MAP = dict(CATEGORIES)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    resources = db.relationship('Resource', backref='author', lazy='dynamic',
                                cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class Resource(db.Model):
    __tablename__ = 'resources'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    link        = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject     = db.Column(db.String(100), nullable=True)
    category    = db.Column(db.String(50), nullable=False, default='other')
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @property
    def category_label(self) -> str:
        return CATEGORY_MAP.get(self.category, self.category.capitalize())

    @property
    def short_description(self) -> str:
        if self.description and len(self.description) > 160:
            return self.description[:157] + '…'
        return self.description or ''

    def __repr__(self) -> str:
        return f'<Resource {self.title!r}>'
