from flask import Flask
from flask_socketio import SocketIO, emit
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Scientia Global Chat Server Running"

@socketio.on('connect')
def handle_connect():
    print("A user connected.")

@socketio.on('disconnect')
def handle_disconnect():
    print("A user disconnected.")

@socketio.on('global_message')
def handle_global_message(data):
    print("Global message received:", data)
    # Broadcast the message to everyone
    socketio.emit('global_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
