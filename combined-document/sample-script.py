from flask import Flask, jsonify, render_template
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import datetime
import uuid
import threading
import time


app = Flask(__name__)

# OpenSearch Config (Wazuh)
OPENSEARCH_URL = "https://localhost:9200"
INDEX = "vpn-events"

urllib3.disable_warnings()

# Stable OpenSearch Session
os_session = requests.Session()
os_session.auth = HTTPBasicAuth("admin", "SecretPassword")
os_session.verify = False
os_session.headers.update({
    "Content-Type": "application/json",
    "Connection": "close"
})
os_session.proxies = {
    "http": None,
    "https": None
}

USERS = {
    "alice":   {"status": "disconnected", "session_id": None},
    "bob":     {"status": "disconnected", "session_id": None},
    "charlie": {"status": "disconnected", "session_id": None},
    "david":   {"status": "disconnected", "session_id": None},
    "eve":     {"status": "disconnected", "session_id": None}
}

def now():
    return datetime.datetime.utcnow().isoformat() + "Z"

@app.route("/")
def dashboard():
    return render_template("dashboard.html", users=USERS)

@app.route("/connect/<user>", methods=["POST"])
def connect(user):
    if user not in USERS:
        return jsonify({"error": "Invalid user"}), 400

    if USERS[user]["status"] == "active":
        return jsonify({"message": "Already connected"})

    session_id = str(uuid.uuid4())[:8]

    event = {
        "@timestamp": now(),
        "event_type": "vpn_connect",
        "user": user,
        "session_id": session_id,
        "source": "vpn-poc",
        "action": "connect"
    }

    resp = os_session.post(
        f"{OPENSEARCH_URL}/vpn-events/_doc",
        json=event,
        timeout=10
    )

    USERS[user]["status"] = "active"
    USERS[user]["session_id"] = session_id

    print(f"[LOGIN] {user} | HTTP {resp.status_code}")
    return jsonify({"message": "Connected", "user": user})

@app.route("/disconnect/<user>", methods=["POST"])
def disconnect(user):
    if user not in USERS:
        return jsonify({"error": "Invalid user"}), 400

    if USERS[user]["status"] != "active":
        return jsonify({"message": "User not connected"})

    session_id = USERS[user]["session_id"]

    event = {
        "@timestamp": now(),
        "event_type": "vpn_disconnect",
        "user": user,
        "session_id": session_id,
        "source": "vpn-poc",
        "action": "disconnect"
    }

    resp = os_session.post(
        f"{OPENSEARCH_URL}/vpn-events/_doc",
        json=event,
        timeout=10
    )

    USERS[user]["status"] = "disconnected"
    USERS[user]["session_id"] = None

    print(f"[LOGOUT] {user} | HTTP {resp.status_code}")
    return jsonify({"message": "Disconnected", "user": user})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
