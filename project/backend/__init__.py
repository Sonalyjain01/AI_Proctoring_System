from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
from backend.config import Config  # ✅ Import centralized config

# ✅ Initialize Extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)  # ✅ Load settings from config.py

    # ✅ Initialize Extensions
    db.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    CORS(app)
    JWTManager(app)  # ✅ Initialize JWT

    # ✅ Register Blueprints (APIs)
    from backend.routes import routes
    from backend.auth import auth
    app.register_blueprint(routes, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/auth')

    # ✅ Auto-create database tables if they don’t exist
    with app.app_context():
        db.create_all()

    return app
