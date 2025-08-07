import os
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Initialize Flask app
app = Flask(_name_)
CORS(app)

# Use threading mode for stability
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Handle incoming messages
@socketio.on('send_message')
def handle_send_message(message):
    print(f"Received message: {message}")
    emit('receive_message', message, broadcast=True)
