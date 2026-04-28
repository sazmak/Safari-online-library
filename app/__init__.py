from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
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

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))