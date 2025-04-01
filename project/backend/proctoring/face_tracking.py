import cv2
import numpy as np
import face_recognition
import firebase_admin
from firebase_admin import credentials, db
from gaze_tracking import GazeTracking
from flask_socketio import emit
from backend import socketio  #  WebSocket for live alerts

#  Initialize Firebase (Load Credentials Securely)
cred = credentials.Certificate("your-firebase-key.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://your-project.firebaseio.com"})

#  Load Registered Users' Faces
known_faces = []
known_names = []

# Load multiple registered faces from files
for i in range(1, 3):  # Adjust number based on how many faces you register
    image = face_recognition.load_image_file(f"user_{i}.jpg")
    encoding = face_recognition.face_encodings(image)[0]
    known_faces.append(encoding)
    known_names.append(f"User {i}")

#  Initialize Haarcascade for Face Detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#  Initialize Gaze Tracker
gaze = GazeTracking()

#  Initialize Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Reduce Width
cap.set(4, 480)  # Reduce Height
previous_frame = None
last_face_recognition_time = 0  # Timer for face recognition
alert_sent = {"unauthorized": False, "fake_face": False, "no_face": False}

def send_alert(message, alert_type):
    """ Send alert to Firebase and WebSocket """
    if not alert_sent[alert_type]:  # Avoid multiple alerts for the same event
        ref = db.reference("alerts")
        ref.push({"message": message})
        socketio.emit("proctoring_alert", {"event": alert_type, "details": message})
        alert_sent[alert_type] = True

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gaze.refresh(frame)
    rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB

    #  Face Detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        send_alert("No face detected!", "no_face")  # Alert only once per event
    else:
        alert_sent["no_face"] = False  # Reset alert flag when a face is detected

    #  Face Recognition (Only Every 5 Seconds for Performance)
    current_time = cv2.getTickCount() / cv2.getTickFrequency()
    if current_time - last_face_recognition_time > 5:
        last_face_recognition_time = current_time  # Reset timer

        face_encodings = face_recognition.face_encodings(rgb_frame)
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            name = "Unauthorized"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                cv2.putText(frame, f"Match Found: {name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                alert_sent["unauthorized"] = False  # Reset alert
            else:
                cv2.putText(frame, "Unauthorized", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                send_alert("Unauthorized face detected!", "unauthorized")

    #  Gaze Tracking
    if gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking straight"
    else:
        text = "Gaze not detected"
    cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    #  Liveness Detection (Motion Check)
    if previous_frame is not None:
        frame_diff = cv2.absdiff(previous_frame, gray)
        if np.mean(frame_diff) < 3:  # Low difference means possible fake face
            cv2.putText(frame, "Fake Face Detected!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            send_alert("Fake face detected!", "fake_face")
        else:
            alert_sent["fake_face"] = False  # Reset alert

    previous_frame = gray  # Store the current frame for next iteration

    cv2.imshow("Face Tracking System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
