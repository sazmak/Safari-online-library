import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Пожалуйста, войдите в систему."
    login_manager.login_message_category = "info"

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        from . import models
        db.create_all()
        # Add profile_picture column to existing DBs that predate this column
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(200)"))
                conn.commit()
            except Exception:
                pass

    # Ensure avatar upload directory exists
    avatars_dir = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
