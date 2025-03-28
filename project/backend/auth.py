from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, get_jwt
from werkzeug.security import check_password_hash, generate_password_hash
from backend.models import db, User, OTPStorage, BlacklistedToken  # ✅ Import models
from flask_mail import Message
import os
import random
import datetime
from flask import current_app as app

auth = Blueprint('auth', __name__)

# ✅ Email Sending Function (Now Uses Config from `__init__.py`)
def send_otp(email):
    otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)  # 5-minute expiry

    # ✅ Store OTP in Database
    existing_otp = OTPStorage.query.filter_by(email=email).first()
    if existing_otp:
        db.session.delete(existing_otp)  # Remove old OTP
    new_otp = OTPStorage(email=email, otp=otp, expires_at=expiration_time)
    db.session.add(new_otp)
    db.session.commit()

    # ✅ Send OTP via Email
    msg = Message("Your OTP for Login", sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f"Your OTP is {otp}. It is valid for 5 minutes."
    mail = app.extensions.get('mail')  # Get Flask-Mail instance
    mail.send(msg)
    print(f"📩 OTP Sent to {email}: {otp}")  # Debugging purpose

# ✅ Register New User
@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    existing_user = User.query.filter_by(email=data['email']).first()

    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(data['password'])  # 🔒 Hash password
    new_user = User(email=data['email'], password=hashed_password, role=data['role'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# ✅ Login & Send OTP
@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password, data['password']):  
        send_otp(user.email)  # 🔥 Send OTP
        return jsonify({'message': 'OTP sent to email. Please verify.', 'email': user.email}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

# ✅ Verify OTP & Generate JWT Token
@auth.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    user_otp = data.get('otp')

    otp_entry = OTPStorage.query.filter_by(email=email).first()

    if otp_entry and otp_entry.otp == user_otp and datetime.datetime.utcnow() < otp_entry.expires_at:
        db.session.delete(otp_entry)  # ✅ Remove OTP after successful login
        db.session.commit()

        # ✅ Generate JWT Token
        user = User.query.filter_by(email=email).first()
        access_token = create_access_token(identity={'email': user.email, 'role': user.role}, expires_delta=datetime.timedelta(hours=1))
        refresh_token = create_refresh_token(identity=user.email)

        return jsonify(access_token=access_token, refresh_token=refresh_token, role=user.role)
    
    return jsonify({'error': 'Invalid or expired OTP'}), 401

# ✅ Logout User (Blacklist Token)
@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  # Get token identifier

    # ✅ Store Blacklisted Token in Database
    blacklisted_token = BlacklistedToken(jti=jti)
    db.session.add(blacklisted_token)
    db.session.commit()

    return jsonify({'message': 'Logged out successfully'}), 200

# ✅ Refresh JWT Token
@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token)

# ✅ Protected Route (For Logged-In Users)
@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
