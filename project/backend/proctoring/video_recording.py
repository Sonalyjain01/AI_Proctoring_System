import cv2
import time
import boto3
import os
import threading
from flask_socketio import emit
from backend import socketio  #  WebSocket for live alerts

#  Load AWS S3 Configuration from Environment Variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "your-s3-bucket")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

VIDEO_FILE = "output.mp4"

#  Initialize video capture (Optimized for 4GB RAM)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Reduce resolution for better performance
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS to save CPU

#  Use MP4 (H.264) for better compression
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(VIDEO_FILE, fourcc, 10, (320, 240))

start_time = time.time()

#  Notify Admin via WebSocket (Recording Started)
socketio.emit("proctoring_alert", {"event": "video_recording", "details": "Video recording started"})

def upload_to_s3():
    """ Upload recorded video to AWS S3 & delete local file after upload """
    try:
        s3_client = boto3.client("s3", aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)
        s3_client.upload_file(VIDEO_FILE, S3_BUCKET_NAME, f"recordings/{VIDEO_FILE}")
        print(" Video uploaded successfully to S3")

        #  Notify Admin via WebSocket (Upload Complete)
        socketio.emit("proctoring_alert", {"event": "video_uploaded", "details": "Video uploaded to S3"})

        #  Delete local file after upload
        os.remove(VIDEO_FILE)
        print("🗑 Local video deleted to save space")

    except Exception as e:
        print(f" Error uploading video: {e}")
        socketio.emit("proctoring_alert", {"event": "upload_failed", "details": f"Failed to upload video: {e}"})

while time.time() - start_time < 30:  #  Record for 30 seconds
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)

cap.release()
out.release()

#  Notify Admin via WebSocket (Recording Complete)
socketio.emit("proctoring_alert", {"event": "video_recording", "details": "Video recording complete"})

#  Upload in a separate thread (Prevents UI lag)
threading.Thread(target=upload_to_s3).start()
