from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.system_event import SystemEvent


WINDOW_MINUTES = 15
ANOMALY_THRESHOLD = 6


def detect_anomaly(db: Session, tenant_id: str):

    window_start = datetime.utcnow() - timedelta(minutes=WINDOW_MINUTES)

    events = (
        db.query(SystemEvent)
        .filter(
            SystemEvent.tenant_id == tenant_id,
            SystemEvent.created_at >= window_start,
        )
        .all()
    )

    escalation_count = sum(
        1 for e in events if "escalated" in e.event_type
    )

    quarantine_count = sum(
        1 for e in events if "quarantined" in e.event_type
    )

    signal_strength = escalation_count + quarantine_count

    if signal_strength >= ANOMALY_THRESHOLD:
        status = "anomalous"
    elif signal_strength >= 3:
        status = "unstable"
    else:
        status = "normal"

    return {
        "status": status,
        "signals": signal_strength,
        "window_minutes": WINDOW_MINUTES,
    }
