#!/bin/bash

# Move to Project Root (if script is run elsewhere)
cd "$(dirname "$0")"

# Start Flask Backend
echo " Starting Flask Backend..."
cd backend
if [ ! -d "venv" ]; then
    echo " Virtual Environment Not Found! Run: python -m venv venv"
    exit 1
fi
source venv/bin/activate
python app.py --host=0.0.0.0 --port=5000 > logs/flask.log 2>&1 &
FLASK_PID=$!

# Start Face Tracking
echo " Starting Face Tracking..."
python face_tracking.py > logs/face_tracking.log 2>&1 &
FACE_TRACKING_PID=$!

# Start Voice Detection
echo " Starting Voice Detection..."
python voice_detection.py > logs/voice_detection.log 2>&1 &
VOICE_DETECTION_PID=$!

# Start React Frontend
echo " Starting React Frontend..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo " Installing React Dependencies..."
    npm install
fi
npm start > logs/react.log 2>&1 &
REACT_PID=$!

# Wait for all processes
echo " AI Proctoring System is LIVE!"
echo " Flask PID: $FLASK_PID"
echo " Face Tracking PID: $FACE_TRACKING_PID"
echo " Voice Detection PID: $VOICE_DETECTION_PID"
echo " React PID: $REACT_PID"

# Function to clean up on exit
cleanup() {
    echo " Stopping Services..."
    kill $FLASK_PID
    kill $FACE_TRACKING_PID
    kill $VOICE_DETECTION_PID
    kill $REACT_PID
    echo " All Services Stopped!"
}

# Trap CTRL+C and stop all processes
trap cleanup SIGINT

# Keep the script running
wait
