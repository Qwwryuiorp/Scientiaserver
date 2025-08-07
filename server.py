from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

USERS_FILE = "users.json"
ADMIN_CODE = "777.9"
MAX_MESSAGES = 5

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
    except Exception as e:
        print("Error saving users:", e)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not data or "username" not in data:
        return jsonify({"success": False, "message": "Username required"}), 400

    username = data["username"].strip()
    if not username:
        return jsonify({"success": False, "message": "Username cannot be empty"}), 400

    users = load_users()
    if username in users:
        return jsonify({"success": False, "message": "Username already taken"}), 400

    users[username] = {"messages_sent": 0}
    save_users(users)
    return jsonify({"success": True})

@socketio.on("message")
def handle_message(data):
    if not isinstance(data, dict):
        emit("blocked", {"message": "Invalid message format"}, to=request.sid)
        return

    username = data.get("username")
    message = data.get("message")

    if not username or not isinstance(username, str) or not message or not isinstance(message, str):
        emit("blocked", {"message": "Invalid username or message"}, to=request.sid)
        return

    username = username.strip()
    message = message.strip()

    if not username or not message:
        emit("blocked", {"message": "Username or message cannot be empty"}, to=request.sid)
        return

    users = load_users()

    if username != ADMIN_CODE:
        if username not in users:
            emit("blocked", {"message": "User not registered"}, to=request.sid)
            return

        if users[username]["messages_sent"] >= MAX_MESSAGES:
            emit("blocked", {"message": "Message limit reached"}, to=request.sid)
            return

        users[username]["messages_sent"] += 1
        save_users(users)

    try:
        emit("message", {"username": username, "message": message}, broadcast=True)
    except Exception as e:
        print("Error broadcasting message:", e)
        emit("blocked", {"message": "Server error broadcasting message"}, to=request.sid)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000 allow_unsafe_werkzeug=True )

