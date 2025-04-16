# proctoring/video_recording.py

import cv2
import time
import boto3
import os
import threading
from backend import socketio  # Import shared socket instance

# Load AWS S3 Configuration from Environment Variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET", "your-s3-bucket")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("AWS_SECRET_KEY")


def upload_to_s3(video_file):
    """ Upload recorded video to AWS S3 & delete local file after upload """
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )
        s3_client.upload_file(video_file, S3_BUCKET_NAME, f"recordings/{video_file}")
        print("✅ Video uploaded to S3.")

        # Notify via WebSocket
        socketio.emit("proctoring_alert", {
            "event": "video_uploaded",
            "details": f"{video_file} uploaded to S3"
        })

        os.remove(video_file)
        print("🗑 Local file deleted.")
    except Exception as e:
        print("❌ Upload failed:", e)
        socketio.emit("proctoring_alert", {
            "event": "upload_failed",
            "details": str(e)
        })


@socketio.on("start_video_recording")
def handle_video_recording(data):
    """ Trigger video recording on SocketIO event """
    user_id = data.get("user_id", "unknown")
    filename = f"user_{user_id}_{int(time.time())}.mp4"

    print(f"🎥 Starting video recording for user {user_id}")

    # Setup video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 10)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 10, (320, 240))

    start_time = time.time()

    socketio.emit("proctoring_alert", {
        "event": "video_recording",
        "details": f"Recording started for user {user_id}"
    })

    while time.time() - start_time < 30:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    socketio.emit("proctoring_alert", {
        "event": "video_recording",
        "details": f"Recording complete for user {user_id}"
    })

    # Upload in background
    threading.Thread(target=upload_to_s3, args=(filename,)).start()

if __name__ == "__main__":
    print("⚙️ Running video recording manually...")
    handle_video_recording({"user_id": "manual_test_user"})
