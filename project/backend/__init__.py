# backend/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
from dotenv import load_dotenv
from backend.config import Config

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask extensions (shared across app)
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()

def create_app():
    """Application factory for creating a Flask app instance."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    CORS(app)
    JWTManager(app)

    # ✅ Register Blueprints
    from backend.routes import routes
    from backend.auth import auth
    app.register_blueprint(routes, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/auth')

    # ✅ Import proctoring WebSocket handlers (auto-load via proctoring/__init__.py)
    try:
        import proctoring  # Calls proctoring/__init__.py which loads all socket handlers
        app.logger.info("✅ Proctoring modules registered.")
    except ImportError as e:
        app.logger.warning(f"⚠️ Failed to load proctoring modules: {e}")

    # ✅ Health check route
    @app.route('/')
    def index():
        return {"message": "✅ Flask Backend is running!"}

    # ✅ Auto-create database tables
    with app.app_context():
        db.create_all()

        # Warn if email config is missing
        if not os.getenv("MAIL_USERNAME") or not os.getenv("MAIL_PASSWORD"):
            app.logger.warning("⚠️ MAIL_USERNAME or MAIL_PASSWORD is not set. Email functionality may not work.")

    return app
