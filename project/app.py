import eventlet
eventlet.monkey_patch()  #  Optimize WebSockets for better performance

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
from backend import create_app, socketio  # Import create_app from backend

#  Create Flask App
app = create_app()

import logging

# Set up logging
log_file = "logs/flask.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] - %(message)s")

logging.info("Flask app started.")


#  Run Flask & WebSocket Server
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
