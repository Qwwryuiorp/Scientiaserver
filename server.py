from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

connected_users = {}      # username -> sid
admin_sid = None          # session ID of admin

@socketio.on('connect')
def handle_connect():
    print(f"[CONNECTED] {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    global admin_sid
    sid = request.sid
    to_remove = None

    for username, user_sid in connected_users.items():
        if user_sid == sid:
            to_remove = username
            break

    if to_remove:
        del connected_users[to_remove]
        if sid == admin_sid:
            admin_sid = None
            print("[ADMIN] Admin disconnected.")
        else:
            print(f"[DISCONNECTED] {to_remove}")

@socketio.on('register_username')
def handle_register_username(data):
    global admin_sid
    username = data.get("username")

    if not username:
        return

    sid = request.sid

    if username == "777.9":
        admin_sid = sid
        connected_users["ADMIN"] = sid
        print(f"[ADMIN] Admin logged in with SID {sid}")
        emit("register_success", {"status": "admin"})
    else:
        if username in connected_users:
            emit("register_fail", {"reason": "Username already taken"})
            return
        connected_users[username] = sid
        print(f"[REGISTERED] {username}")
        emit("register_success", {"status": "user"})

@socketio.on('send_message')
def handle_send_message(data):
    sender = data.get("from")
    recipient = data.get("to")
    message = data.get("message")
    sid = request.sid

    if sid == admin_sid:
        # Broadcast to everyone except admin
        print(f"[ADMIN BROADCAST] {message}")
        for user, user_sid in connected_users.items():
            if user_sid != admin_sid:
                emit("receive_message", {
                    "from": "ADMIN",
                    "message": message
                }, room=user_sid)
        return

    # For normal users
    recipient_sid = connected_users.get(recipient)
    if recipient_sid:
        print(f"[MESSAGE] {sender} → {recipient}: {message}")
        emit("receive_message", {
            "from": sender,
            "message": message
        }, room=recipient_sid)
    else:
        print(f"[ERROR] Recipient '{recipient}' not connected")
        emit("error", {"message": f"User '{recipient}' not available"})

if _name_ == "_main_":
    import os
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
