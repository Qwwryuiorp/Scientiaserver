from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Create the socket with cors allowed
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to track connected users
connected_users = {}

# Broadcast a message to all clients
def broadcast_message(message):
    emit('receive_message', message, broadcast=True)

# When a user connects
@socketio.on('connect')
def handle_connect():
    print("Client connected")

# When a user disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
    for username, sid in list(connected_users.items()):
        if sid == request.sid:
            del connected_users[username]
            break

# Handle login and store the user's session
@socketio.on('login')
def handle_login(data):
    username = data.get('username')
    if username:
        connected_users[username] = request.sid
        print(f"{username} logged in with SID {request.sid}")

# Handle messages
@socketio.on('send_message')
def handle_send_message(data):
    sender = data.get('from')
    recipient = data.get('to')
    message = data.get('message')

    if sender == "777.9":  # Admin user sends globally
        print(f"[ADMIN GLOBAL] {message}")
        broadcast_message({'from': 'ADMIN', 'message': message})
    elif recipient in connected_users:
        sid = connected_users[recipient]
        emit('receive_message', {'from': sender, 'message': message}, to=sid)
    else:
        emit('receive_message', {'from': 'SYSTEM', 'message': f'User "{recipient}" not online'}, to=request.sid)

# Start the app
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000)) 
    socketio.run(app, host='0.0.0.0', port=port)
