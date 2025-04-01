import os

class Config:
    """Application Configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'  # ✅ Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")  # ✅ Secret Key from Env
    CORS_HEADERS = 'Content-Type'

    # ✅ Email Configuration (For OTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-email-password")
