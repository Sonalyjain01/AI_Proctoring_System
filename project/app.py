# backend/app.py

import os
import eventlet
eventlet.monkey_patch()  # Enable WebSocket support for Flask-SocketIO

from dotenv import load_dotenv
load_dotenv()  # Load .env variables

from backend import create_app, socketio

import logging

# Setup logging directory
os.makedirs("logs", exist_ok=True)

# Configure log file
logging.basicConfig(
    filename="logs/flask.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
logging.info("🚀 Starting Flask app...")

# Initialize Flask app
app = create_app()

# Run the app using SocketIO
if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
