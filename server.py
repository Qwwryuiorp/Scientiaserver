from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(_name_)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('send_message')
def handle_send_message(message):
    emit('receive_message', message, broadcast=True)

if _name_ == '_main_':
    socketio.run(app, host='0.0.0.0', port=5000)
