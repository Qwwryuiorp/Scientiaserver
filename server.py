from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@socketio.on('register')
def register_user(data):
    username = data['username']
    sid = request.sid
    users[username] = sid
    print(f"User registered: {username} -> {sid}")

@socketio.on('send_message')
def handle_send_message(data):
    sender = data.get('sender')
    recipient = data.get('recipient')
    message = data.get('message')
    if sender == '777.9':
        for user, sid in users.items():
            if sid != request.sid:
                emit('receive_message', {'sender': 'ADMIN', 'message': message}, room=sid)
    elif recipient == 'GLOBAL':
        for user, sid in users.items():
            if sid != request.sid:
                emit('receive_message', {'sender': sender, 'message': message}, room=sid)
    else:
        recipient_sid = users.get(recipient)
        if recipient_sid:
            emit('receive_message', {'sender': sender, 'message': message}, room=recipient_sid)

if __name__ == '__main__':
    socketio.run(app, port=5000)
