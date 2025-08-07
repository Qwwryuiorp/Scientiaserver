from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Setup Flask app and Socket.IO
app = Flask(_name_)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store users and their session IDs
connected_users = {}

# Handle connection
@socketio.on('connect')
def on_connect():
    print(f"[CONNECTED] {request.sid}")

# Handle disconnection
@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    for username in list(connected_users):
        if connected_users[username] == sid:
            del connected_users[username]
            print(f"[DISCONNECTED] {username}")
            break

# Register username
@socketio.on('register_username')
def register_username(data):
    username = data.get('username')
    if username:
        connected_users[username] = request.sid
        print(f"[REGISTERED] {username} with SID {request.sid}")

# Send private message
@socketio.on('send_message')
def send_message(data):
    sender = data.get('from')
    recipient = data.get('to')
    message = data.get('message')

    print(f"[MESSAGE] {sender} → {recipient}: {message}")

    recipient_sid = connected_users.get(recipient)
    if recipient_sid:
        emit('receive_message', {
            'from': sender,
            'message': message
        }, room=recipient_sid)
    else:
        print(f"[ERROR] {recipient} not connected.")

# Run the server on default or system-assigned port
if _name_ == '_main_':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

