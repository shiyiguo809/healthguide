from flask import Flask, request, jsonify, send_from_directory
import os, io, statistics, json
from datetime import datetime, timedelta
from collections import defaultdict
import anthropic

app = Flask(__name__, static_folder="static")
health_data_store = {}
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/demo", methods=["POST"])
def load_demo():
    import random
    random.seed(42)
    today = datetime.today()
    parsed = {}
    for i in range(60):
        date = (today - timedelta(days=59-i)).strftime("%Y-%m-%d")
        parsed[date] = {
            "HKQuantityTypeIdentifierHeartRate": round(random.gauss(72,8),1),
            "HKQuantityTypeIdentifierOxygenSaturation": round(random.gauss(97,1.5),1),
            "HKQuantityTypeIdentifierStepCount": int(random.gauss(5500,2000)),
            "HKQuantityTypeIdentifierActiveEnergyBurned": round(random.gauss(280,80),1),
            "HKQuantityTypeIdentifierBloodPressureSystolic": round(random.gauss(125,10),1),
            "HKQuantityTypeIdentifierBloodPressureDiastolic": round(random.gauss(78,8),1),
            "HKCategoryTypeIdentifierSleepAnalysis": round(random.gauss(7.2,1.0),1),
        }
    health_data_store["data"] = parsed
    health_data_store["alerts"] = []
    return jsonify({"success": True, "days": len(parsed), "alerts": 0})

@app.route("/api/health-data")
def get_health_data():
    return jsonify({"data": health_data_store.get("data",{}), "alerts": [], "thresholds": {
        "HKQuantityTypeIdentifierHeartRate": {"name":"Heart Rate","unit":"bpm","icon":"❤️"},
        "HKQuantityTypeIdentifierOxygenSaturation": {"name":"Blood Oxygen","unit":"%","icon":"🫁"},
        "HKQuantityTypeIdentifierStepCount": {"name":"Daily Steps","unit":"steps","icon":"👟"},
        "HKQuantityTypeIdentifierActiveEnergyBurned": {"name":"Active Calories","unit":"kcal","icon":"🔥"},
        "HKQuantityTypeIdentifierBloodPressureSystolic": {"name":"Systolic BP","unit":"mmHg","icon":"🩸"},
        "HKQuantityTypeIdentifierBloodPressureDiastolic": {"name":"Diastolic BP","unit":"mmHg","icon":"🩸"},
        "HKCategoryTypeIdentifierSleepAnalysis": {"name":"Sleep","unit":"hrs","icon":"😴"},
    }})

@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.json or {}
    msg = body.get("message","").strip()
    if not ANTHROPIC_API_KEY:
        return jsonify({"reply": "Add your ANTHROPIC_API_KEY to enable AI chat!"})
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    res = client.messages.create(model="claude-haiku-4-5", max_tokens=400,
        system="You are a friendly health assistant for older adults. Speak simply and warmly.",
        messages=[{"role":"user","content":msg}])
    return jsonify({"reply": res.content[0].text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
