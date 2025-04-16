# proctoring/face_tracking.py

import cv2
import numpy as np
import face_recognition
import time
import threading
import os
from backend import socketio
from gaze_tracking import GazeTracking

# Optional Firebase setup
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_ENABLED = True
except ImportError:
    FIREBASE_ENABLED = False
    print("⚠️ Firebase not installed, skipping DB alerts.")

# Firebase init
if FIREBASE_ENABLED:
    try:
        cred = credentials.Certificate("your-firebase-key.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://your-project.firebaseio.com"
        })
    except Exception as e:
        print("❌ Firebase init error:", e)
        FIREBASE_ENABLED = False

# Load known faces (mock logic)
known_faces = []
known_names = []
for i in range(1, 3):
    try:
        image = face_recognition.load_image_file(f"user_{i}.jpg")
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(f"User {i}")
    except Exception as e:
        print(f"⚠️ Error loading user_{i}.jpg: {e}")

# Alert state tracker
alert_sent = {"unauthorized": False, "fake_face": False, "no_face": False}


def send_alert(message, alert_type):
    """ Send alert to Firebase and WebSocket """
    if not alert_sent.get(alert_type, False):
        print(f"🚨 {alert_type.upper()}: {message}")

        if FIREBASE_ENABLED:
            try:
                ref = db.reference("alerts")
                ref.push({"message": message})
            except Exception as e:
                print("❌ Firebase push failed:", e)

        socketio.emit("proctoring_alert", {
            "event": alert_type,
            "details": message
        })
        alert_sent[alert_type] = True


def track_face(user_id="unknown"):
    """ Core function to start face & gaze tracking """
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    previous_frame = None
    last_face_recognition_time = 0
    gaze = GazeTracking()

    print("🎥 Face tracking started.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb_frame = frame[:, :, ::-1]
        gaze.refresh(frame)

        # Face Detection
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1,
                                              minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            send_alert("No face detected!", "no_face")
        else:
            alert_sent["no_face"] = False

        # Face Recognition every 5 seconds
        current_time = time.time()
        if current_time - last_face_recognition_time > 5:
            last_face_recognition_time = current_time

            encodings = face_recognition.face_encodings(rgb_frame)
            for face_encoding in encodings:
                matches = face_recognition.compare_faces(known_faces, face_encoding)
                if True in matches:
                    alert_sent["unauthorized"] = False
                else:
                    send_alert("Unauthorized face detected!", "unauthorized")

        # Gaze Tracking
        if gaze.is_right():
            gaze_text = "Looking right"
        elif gaze.is_left():
            gaze_text = "Looking left"
        elif gaze.is_center():
            gaze_text = "Looking center"
        else:
            gaze_text = "Gaze undetected"

        cv2.putText(frame, gaze_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Liveness Detection (motion)
        if previous_frame is not None:
            diff = cv2.absdiff(previous_frame, gray)
            if np.mean(diff) < 3:
                send_alert("Fake face detected (no motion)", "fake_face")
            else:
                alert_sent["fake_face"] = False

        previous_frame = gray

        # Show live feed (optional for debugging)
        cv2.imshow("Proctoring - Face Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


@socketio.on("start_face_tracking")
def handle_start_face_tracking(data):
    """ Trigger face tracking via WebSocket """
    user_id = data.get("user_id", "unknown")
    print(f"🧠 Starting face tracking for user {user_id}")
    threading.Thread(target=track_face, args=(user_id,)).start()


if __name__ == "__main__":
    print("⚙️ Running face tracking manually...")
    track_face("manual_test_user")
