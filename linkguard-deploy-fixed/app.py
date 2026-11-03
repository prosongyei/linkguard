# Python, app.py, Python 3.10+, Flask
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
import json

app = Flask(__name__)

EVENT_FILE = Path("events.json")
lock = Lock()


def record_event(event):
    with lock:
        events = json.loads(
            EVENT_FILE.read_text()
            if EVENT_FILE.exists() else "[]"
        )
        events.append(event)
        EVENT_FILE.write_text(json.dumps(events, indent=2))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/click", methods=["POST"])
def click():
    data = request.get_json(silent=True) or {}

    if data.get("consent") is not True:
        return jsonify({"error": "Consent required"}), 403

    record_event({
        "time": datetime.now(timezone.utc).isoformat(),
        "event": "authorized_test_click",
        "campaign": str(data.get("campaign", "demo"))[:50]
    })

    return jsonify({
        "status": "recorded",
        "message": "Security demonstration completed."
    })


@app.route("/events")
def events():
    if not EVENT_FILE.exists():
        return jsonify([])

    return jsonify(json.loads(EVENT_FILE.read_text()))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)