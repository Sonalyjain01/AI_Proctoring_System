from backend import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlalchemy.types as types
import pickle

# ✅ Custom Data Type for Face Encodings (Stores as Pickle)
class PickleType(types.TypeDecorator):
    impl = types.LargeBinary

    def process_bind_param(self, value, dialect):
        return pickle.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return pickle.loads(value) if value is not None else None

# ✅ User Model (Stores Admin & Student Information)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_locked = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # 'admin' or 'student'

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ✅ Exam Model (Stores Exam Details)
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Proctoring Logs (Stores Cheating Alerts)
class ProctoringLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(255), nullable=False)  # Example: "Face Not Detected"
    event_details = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Face Recognition Data Storage
class FaceRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    face_encoding = db.Column(PickleType, nullable=False)  # Stores face encoding as PickleType

# ✅ Video Recording Metadata (Stores Video File Info)
class VideoRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_to_cloud = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Session Token Management (Handles User Sessions)
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def logout(self):
        self.is_active = False
        self.logout_time = datetime.utcnow()

# ✅ OTP Storage (For Multi-Factor Authentication)
class OTPStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), db.ForeignKey('user.email'), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=False)  # 6-digit OTP
    expires_at = db.Column(db.DateTime, nullable=False)  # Expiry Time (5 mins)

# ✅ Blacklisted JWT Tokens (For Secure Logout Handling)
class BlacklistedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), nullable=False, unique=True)  # Unique JWT Token ID
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Initialize Database
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
