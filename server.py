from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Scientia SocketIO Server Running"

@socketio.on('private_message')
def handle_private_message(data):
    print("Private message received:", data)
    recipient_id = data.get("recipientId")
    socketio.emit('private_message', data, room=recipient_id)

@socketio.on('join')
def on_join(data):
    user_id = data.get("userId")
    join_room(user_id)
    print(f"User {user_id} joined their room")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
