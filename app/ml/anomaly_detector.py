import json
import logging
from datetime import datetime, timedelta

import numpy as np
from sklearn.ensemble import IsolationForest

from app.db.session import get_db
from app.models.governance_event_log import GovernanceEventLog
from app.services.governance_alert_service import create_alert

logger = logging.getLogger("app.audit_anomaly")

BASELINE_DAYS = 30
MIN_EVENTS = 50


def _event_payload(event: GovernanceEventLog) -> dict:
    payload = event.original_payload
    if not payload:
        return {}

    if isinstance(payload, dict):
        return payload

    try:
        return json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return {}


def _event_timestamp(event: GovernanceEventLog) -> datetime:
    return event.created_at or datetime.utcnow()


def _event_control(event: GovernanceEventLog) -> str:
    payload = _event_payload(event)
    return (
        payload.get("control")
        or payload.get("endpoint")
        or event.reason
        or event.event_type
        or "unknown"
    )


def _event_ip(event: GovernanceEventLog) -> str:
    payload = _event_payload(event)
    return payload.get("ip") or payload.get("ip_address") or "unknown"


def create_governance_alert(db, tenant_id: str, score: float) -> None:
    create_alert(
        db,
        tenant_id=tenant_id,
        alert_type="audit_event_anomaly",
        severity="high",
        message=f"Audit event anomaly detected with score {score:.4f}",
    )
    db.commit()


def extract_features(events):
    if not events:
        return None

    timestamps = [_event_timestamp(e) for e in events]
    controls = [_event_control(e) for e in events]
    event_types = [e.event_type or "unknown" for e in events]
    ips = [_event_ip(e) for e in events]

    total = len(events)
    unique_controls = len(set(controls))
    evidence_uploads = event_types.count("evidence_upload")
    unique_ips = len(set(ips))
    access_reviews = event_types.count("access_review")
    off_hours = sum(1 for t in timestamps if t.hour < 5)
    off_hour_ratio = off_hours / total
    new_ip_ratio = unique_ips / total

    intervals = []
    timestamps_sorted = sorted(timestamps)
    for i in range(1, len(timestamps_sorted)):
        delta = (timestamps_sorted[i] - timestamps_sorted[i - 1]).total_seconds()
        intervals.append(delta)

    avg_interval = np.mean(intervals) if intervals else 0

    return np.array(
        [
            total,
            unique_controls,
            evidence_uploads,
            access_reviews,
            off_hour_ratio,
            new_ip_ratio,
            avg_interval,
        ]
    )


def run_tenant_anamoly_detection(tenant_id):
    db = next(get_db())

    try:
        now = datetime.utcnow()
        baseline_start = now - timedelta(days=BASELINE_DAYS)
        recent_start = now - timedelta(days=7)

        baseline_events = (
            db.query(GovernanceEventLog)
            .filter(
                GovernanceEventLog.tenant_id == tenant_id,
                GovernanceEventLog.created_at >= baseline_start,
            )
            .all()
        )

        recent_events = (
            db.query(GovernanceEventLog)
            .filter(
                GovernanceEventLog.tenant_id == tenant_id,
                GovernanceEventLog.created_at >= recent_start,
            )
            .all()
        )

        if len(baseline_events) < MIN_EVENTS or len(recent_events) < 5:
            return

        baseline_vectors = []
        day_map = {}

        for event in baseline_events:
            day = _event_timestamp(event).date()
            day_map.setdefault(day, []).append(event)

        for events in day_map.values():
            vec = extract_features(events)
            if vec is not None:
                baseline_vectors.append(vec)

        if len(baseline_vectors) < 7:
            return

        model = IsolationForest(contamination=0.05)
        model.fit(np.array(baseline_vectors))

        recent_vector = extract_features(recent_events)
        if recent_vector is None:
            return

        recent_vector = recent_vector.reshape(1, -1)
        score = model.decision_function(recent_vector)[0]
        prediction = model.predict(recent_vector)[0]

        if prediction == -1:
            create_governance_alert(db, tenant_id, score)
            logger.warning(
                "audit_event_anomaly_detected",
                extra={"tenant_id": tenant_id, "score": float(score)},
            )
    finally:
        db.close()


def run_tenant_anomaly_detection(tenant_id):
    return run_tenant_anamoly_detection(tenant_id)
