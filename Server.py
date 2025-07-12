from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
messages = {}

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    to = data["to"]
    msg = {
        "from": data["from"],
        "text": data["text"],
        "time": datetime.utcnow().isoformat()
    }
    messages.setdefault(to, []).append(msg)
    return jsonify({"status": "sent"})

@app.route("/receive/<receiver>", methods=["GET"])
def receive(receiver):
    msg_list = messages.pop(receiver, [])
    return jsonify(msg_list)

@app.route("/ping", methods=["GET"])
def ping():
    return "Scientia relay active."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
