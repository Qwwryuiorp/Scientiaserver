from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # username -> password
user_sessions = {}  # sid -> username

def is_valid_username(username):
    return 1 <= len(username) <= 32

@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Welcome!'})

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    username = user_sessions.get(sid)
    if username:
        print(f"User disconnected: {username} ({sid})")
        # Remove user from session and leave room
        leave_room(username)
        del user_sessions[sid]
    else:
        print(f"Unknown client disconnected: {sid}")

@socketio.on('signup')
def handle_signup(username, password):
    sid = request.sid
    print(f"Signup attempt: {username}")

    if not is_valid_username(username):
        emit('signup_response', {'success': False, 'error': 'Invalid username.'})
        return

    if username in users:
        emit('signup_response', {'success': False, 'error': 'Username already exists.'})
        return

    users[username] = password
    print(f"User registered: {username}")
    emit('signup_response', {'success': True})

@socketio.on('login')
def handle_login(username, password):
    sid = request.sid
    print(f"Login attempt: {username}")

    if username not in users:
        emit('login_response', {'success': False, 'error': 'User does not exist.'})
        return

    if users[username] != password:
        emit('login_response', {'success': False, 'error': 'Incorrect password.'})
        return

    user_sessions[sid] = username
    join_room(username)  # join a private room named by the username
    print(f"User logged in: {username}")
    emit('login_response', {'success': True})

@socketio.on('send_message')
def handle_send_message(to_user, message):
    sid = request.sid
    from_user = user_sessions.get(sid)
    if not from_user:
        emit('error', {'error': 'You must be logged in to send messages.'})
        return

    if not to_user or not message:
        emit('error', {'error': 'Recipient and message required.'})
        return

    if to_user not in users:
        emit('error', {'error': f'User {to_user} does not exist.'})
        return

    print(f"Message from {from_user} to {to_user}: {message}")

    # Emit message ONLY to recipient's room
    socketio.emit('receive_message', [from_user, message], room=to_user)

    # Optionally emit message back to sender's client too (for local display)
    socketio.emit('receive_message', [from_user, message], room=from_user)

    emit('message_sent', {'to': to_user, 'message': message})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
