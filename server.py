from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

USERS_FILE = "users.json"
ADMIN_CODE = "777.9"
MAX_MESSAGES = 5

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    users = load_users()

    if username in users:
        return jsonify({"success": False, "message": "Username already taken"}), 400

    users[username] = {"messages_sent": 0}
    save_users(users)
    return jsonify({"success": True})

@socketio.on("message")
def handle_message(data):
    username = data.get("username")
    message = data.get("message")

    users = load_users()

    if username not in users:
        return

    if username != ADMIN_CODE:
        if users[username]["messages_sent"] >= MAX_MESSAGES:
            emit("blocked", {"message": "Limit reached"}, to=request.sid)
            return
        users[username]["messages_sent"] += 1
        save_users(users)

    emit("message", {"username": username, "message": message}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
