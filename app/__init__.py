import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
    })

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message = "Пожалуйста, войдите в систему."
    login_manager.login_message_category = "info"

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        from . import models
        db.create_all()

    avatars_dir = os.path.join(app.root_path, "static", "uploads", "avatars")
    os.makedirs(avatars_dir, exist_ok=True)

    return app


@login_manager.user_loader
def load_user(user_id: str):
    from .models import User
    return db.session.get(User, int(user_id))
