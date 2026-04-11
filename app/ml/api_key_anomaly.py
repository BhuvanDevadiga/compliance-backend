import json
import time
import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from app.core.redis_client import redis_client

logger = logging.getLogger("app.api_key_anomaly")

BASELINE_WINDOW = 7 * 24 * 60 * 60
RECENT_WINDOW = 30 * 60  


def compute_header_anomaly_score(events):
    if not events:
        return 0.0

    total = len(events)
    anomalies = 0

    for e in events:
        if e.get("header_anomaly") == 1:
            anomalies += 1

    return anomalies / total


def extract_features(events):
    payloads = []
    latencies = []
    hours = []
    endpoints = {}
    parsed_events = []

    for raw in events:
        data = json.loads(raw)
        parsed_events.append(data)
        payloads.append(data["payload_size"])
        latencies.append(data["latency"])
        hours.append(data["hour"])

        ep = data["endpoint"]
        endpoints[ep] = endpoints.get(ep, 0) + 1

    header_anomaly_score = compute_header_anomaly_score(parsed_events)

    features = [
        len(events),
        np.mean(payloads) if payloads else 0,
        np.mean(latencies) if latencies else 0,
        np.std(payloads) if payloads else 0,
        np.std(latencies) if latencies else 0,
        len(endpoints),
        np.mean(hours) if hours else 0,
        header_anomaly_score,
    ]

    return np.array(features)


def analyze_key(hashed_key):
    now = int(time.time())

    key = f"api_key_events:{hashed_key}"

    baseline_start = now - BASELINE_WINDOW
    recent_start = now - RECENT_WINDOW

    baseline_events = redis_client.zrangebyscore(key, baseline_start, now)
    recent_events = redis_client.zrangebyscore(key, recent_start, now)

    if len(baseline_events) < 50 or len(recent_events) < 5:
        return

    baseline_vectors = []
    chunk_size = max(len(baseline_events) // 10, 10)

    for i in range(0, len(baseline_events), chunk_size):
        chunk = baseline_events[i:i+chunk_size]
        baseline_vectors.append(extract_features(chunk))

    X_baseline = np.array(baseline_vectors)
    X_recent = extract_features(recent_events).reshape(1, -1)

    model = IsolationForest(contamination=0.05)
    model.fit(X_baseline)

    pred = model.predict(X_recent)

    if pred[0] == -1:
        redis_client.setex(f"api_key_anomaly:{hashed_key}", 3600, 1)
        logger.warning("api_key_anomaly_detected", extra={"api_key": hashed_key})
