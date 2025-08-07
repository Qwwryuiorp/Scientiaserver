 import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Create Flask app
app = Flask(_name_)
CORS(app)

# Create Socket.IO server with CORS allowed
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to store connected users and their Socket.IO session IDs
connected_users = {}

# When a user connects
@socketio.on('connect')
def handle_connect():
    print(f"[CONNECTED] Client connected: {request.sid}")

# When a user disconnects
@socketio.on('disconnect')
def handle_disconnect():
    disconnected_sid = request.sid
    username_to_remove = None

    # Find and remove user by sid
    for username, sid in connected_users.items():
        if sid == disconnected_sid:
            username_to_remove = username
            break
    if username_to_remove:
        del connected_users[username_to_remove]
        print(f"[DISCONNECTED] {username_to_remove} disconnected.")

# When a user logs in or registers
@socketio.on('register_username')
def handle_register_username(data):
    username = data.get('username')
    if username:
        connected_users[username] = request.sid
        print(f"[REGISTER] {username} registered with SID {request.sid}")

# When sending a private message
@socketio.on('send_message')
def handle_send_message(data):
    sender = data.get('from')
    recipient = data.get('to')
    message = data.get('message')

    print(f"[MESSAGE] From {sender} to {recipient}: {message}")

    recipient_sid = connected_users.get(recipient)
    if recipient_sid:
        emit('receive_message', {
            'from': sender,
            'message': message
        }, room=recipient_sid)
    else:
        print(f"[ERROR] Recipient {recipient} not connected.")

# Run the server
if _name_ == '_main_':
    socketio.run(app, host='0.0.0.0', port=5000)
