from backend import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlalchemy.types as types
import pickle

# ✅ Custom Pickle Type for Face Encodings
class PickleType(types.TypeDecorator):
    impl = types.LargeBinary

    def process_bind_param(self, value, dialect):
        return pickle.dumps(value) if value else None

    def process_result_value(self, value, dialect):
        return pickle.loads(value) if value else None

# ✅ User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_locked = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default="student")  # admin | student

    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ✅ Exam Schedule
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_duration = db.Column(db.Integer, nullable=False)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Logs Detected by Proctoring AI
class ProctoringLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(255), nullable=False)
    event_details = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Stored Encodings for Face Recognition
class FaceRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    face_encoding = db.Column(PickleType, nullable=False)

# ✅ Video Upload Records
class VideoRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_to_cloud = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Login Session Tracking
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def logout(self):
        self.is_active = False
        self.logout_time = datetime.utcnow()

# ✅ OTP Handling for MFA
class OTPStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), db.ForeignKey('user.email'), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

# ✅ JWT Token Blacklist
class BlacklistedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), nullable=False, unique=True)
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Manual DB Init
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
