from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Exam, ProctoringLog, VideoRecord, Session

routes = Blueprint('routes', __name__)

# ✅ API: Fetch All Users (Admin Only) with Pagination
@routes.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    user_list = [{"id": user.id, "email": user.email, "role": user.role} for user in users.items]

    return jsonify({
        "users": user_list,
        "total_pages": users.pages,
        "current_page": users.page
    })

# ✅ API: Fetch Individual User Details (Admin Only)
@routes.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({"id": user.id, "email": user.email, "role": user.role})

# ✅ API: Fetch All Exams (Admin & Student)
@routes.route('/exams', methods=['GET'])
@jwt_required()
def get_exams():
    exams = Exam.query.all()
    exam_list = [{"id": exam.id, "subject": exam.subject, "start_time": exam.start_time, "end_time": exam.end_time, "total_duration": exam.total_duration} for exam in exams]
    return jsonify(exam_list)

# ✅ API: Create Exam (Admin Only) with Validation
@routes.route('/exams', methods=['POST'])
@jwt_required()
def create_exam():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json

    # ✅ Validate Data
    required_fields = ["subject", "start_time", "end_time", "total_duration"]
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # ✅ Prevent Overlapping Exams
    existing_exam = Exam.query.filter(
        (Exam.start_time <= data['end_time']) & (Exam.end_time >= data['start_time'])
    ).first()

    if existing_exam:
        return jsonify({'error': 'Exam time overlaps with an existing exam'}), 400

    # ✅ Create Exam
    new_exam = Exam(
        subject=data['subject'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        total_duration=data['total_duration']
    )
    db.session.add(new_exam)
    db.session.commit()

    return jsonify({'message': 'Exam created successfully'}), 201

# ✅ API: Delete an Exam (Admin Only)
@routes.route('/exams/<int:exam_id>', methods=['DELETE'])
@jwt_required()
def delete_exam(exam_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    exam = Exam.query.get(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    db.session.delete(exam)
    db.session.commit()

    return jsonify({'message': 'Exam deleted successfully'}), 200

# ✅ API: Fetch Proctoring Logs (Admin Only) with Pagination & Sorting
@routes.route('/proctoring_logs', methods=['GET'])
@jwt_required()
def get_proctoring_logs():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    logs = ProctoringLog.query.order_by(ProctoringLog.detected_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    log_list = [{"id": log.id, "event_type": log.event_type, "details": log.event_details, "timestamp": log.detected_at} for log in logs.items]

    return jsonify({
        "logs": log_list,
        "total_pages": logs.pages,
        "current_page": logs.page
    })

# ✅ API: Fetch Video Records (Admin Only)
@routes.route('/video_records', methods=['GET'])
@jwt_required()
def get_video_records():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    videos = VideoRecord.query.all()
    video_list = [{"id": video.id, "user_id": video.user_id, "file_name": video.file_name, "file_path": video.file_path, "uploaded_to_cloud": video.uploaded_to_cloud, "timestamp": video.timestamp} for video in videos]
    return jsonify(video_list)

# ✅ API: Fetch Active Sessions (Admin Only)
@routes.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    sessions = Session.query.filter_by(is_active=True).all()
    session_list = [{"id": session.id, "user_id": session.user_id, "login_time": session.login_time, "logout_time": session.logout_time, "is_active": session.is_active} for session in sessions]
    return jsonify(session_list)

# ✅ API: Fetch Real-Time Active Students (Admin Only)
@routes.route('/live_students', methods=['GET'])
@jwt_required()
def get_live_students():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    active_students = Session.query.filter_by(is_active=True).all()
    student_list = [{"user_id": session.user_id, "login_time": session.login_time} for session in active_students]

    return jsonify(student_list)
