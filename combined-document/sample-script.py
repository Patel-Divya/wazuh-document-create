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
INDEX = "vpn-sessions"

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

# Fixed Users for POC
USERS = {
    "alice":   {"status": "disconnected", "session_id": None},
    "bob":     {"status": "disconnected", "session_id": None},
    "charlie": {"status": "disconnected", "session_id": None},
    "david":   {"status": "disconnected", "session_id": None},
    "eve":     {"status": "disconnected", "session_id": None}
}

# Helpers
def now():
    return datetime.datetime.utcnow().isoformat() + "Z"

# Bandwidth Accounting (MOCK)
def get_bandwidth_usage(ip, start_time, end_time=None):
    """
    Placeholder for future Elastic / NMS query.
    For now returns mock data.
    """
    # TODO: Replace with real query
    return {
        "bytes_in": 512 * 1024 * 1024,   # 512 MB
        "bytes_out": 512 * 1024 * 1024,  # 512 MB
    }

def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024 ** 3), 3)

def update_active_sessions():
    for user, info in USERS.items():
        if info["status"] != "active":
            continue

        session_id = info["session_id"]
        now_time = now()

        # ---- MOCK BANDWIDTH DELTA ----
        usage = get_bandwidth_usage(
            ip="mock-ip",
            start_time="mock-last",
            end_time=now_time
        )

        delta_in = usage["bytes_in"]
        delta_out = usage["bytes_out"]

        # Update ES (incremental)
        update_doc = {
            "script": {
                "source": """
                    ctx._source.bytes_in += params.in;
                    ctx._source.bytes_out += params.out;
                    ctx._source.bandwidth_gb =
                        (ctx._source.bytes_in + ctx._source.bytes_out) / 1024 / 1024 / 1024;
                    ctx._source.last_accounted_at = params.now;
                """,
                "lang": "painless",
                "params": {
                    "in": delta_in,
                    "out": delta_out,
                    "now": now_time
                }
            }
        }

        resp = os_session.post(
            f"{OPENSEARCH_URL}/{INDEX}/_update/{user}-{session_id}",
            json=update_doc,
            timeout=10
        )

        print(f"[ACCOUNTING] {user} +{bytes_to_gb(delta_in + delta_out)} GB | HTTP {resp.status_code}")

def accounting_worker():
    while True:
        try:
            time.sleep(120)  # 2 minutes
            update_active_sessions()
        except Exception as e:
            print("[ACCOUNTING ERROR]", e)

# Routes
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

    doc = {
        "@timestamp": now(),
        "user": user,
        "session_id": session_id,
        # "private_ip": private_ip,
        "status": "active",
        "login_time": now(),
        "logout_time": None

         # Bandwidth
        # "bytes_in": 0,
        # "bytes_out": 0,
        # "bandwidth_gb": 0.0,
    }

    resp = os_session.put(
        f"{OPENSEARCH_URL}/{INDEX}/_doc/{user}-{session_id}?refresh=true",
        json=doc,
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

    update_doc = {
        "doc": {
            "status": "closed",
            "logout_time": now()
        }
    }

    resp = os_session.post(
        f"{OPENSEARCH_URL}/{INDEX}/_update/{user}-{session_id}?refresh=true",
        json=update_doc,
        timeout=10
    )

    USERS[user]["status"] = "disconnected"
    USERS[user]["session_id"] = None

    print(f"[LOGOUT] {user} | HTTP {resp.status_code}")
    return jsonify({"message": "Disconnected", "user": user})

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    t = threading.Thread(target=accounting_worker, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
