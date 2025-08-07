import os
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

connected_users = {}
ADMIN_CODE = "777.9"

@socketio.on('connect_user')
def connect_user(data):
    username = data.get("username")
    sid = request.sid
    if username in connected_users and username != ADMIN_CODE:
        emit("error", {"message": "Duplicate username."})
        return
    connected_users[username] = sid
    emit("connected", {"message": f"{username} connected."})

@socketio.on('send_message')
def send_message(data):
    sender = data.get("from")
    recipient = data.get("to")
    message = data.get("message")
    if not sender or not message:
        return
    if sender == ADMIN_CODE:
        if recipient and recipient in connected_users:
            emit("receive_message", {"from": sender, "message": message}, to=connected_users[recipient])
        else:
            emit("receive_message", {"from": sender, "message": message}, broadcast=True)
        return
    if sender not in connected_users:
        emit("error", {"message": "Not authorized."})
        return
    if recipient:
        if recipient in connected_users:
            emit("receive_message", {"from": sender, "message": message}, to=connected_users[recipient])
        else:
            emit("error", {"message": "Recipient not found."})
    else:
        emit("receive_message", {"from": sender, "message": message}, broadcast=True)

@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    for user, user_sid in list(connected_users.items()):
        if user_sid == sid:
            connected_users.pop(user)
            break

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)
