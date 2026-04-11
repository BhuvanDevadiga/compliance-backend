from sqlalchemy.orm import Session
from app.models.mitigation_log import MitigationLog
from datetime import datetime, timedelta


def mitigation_summary(db: Session):

    window = datetime.utcnow() - timedelta(hours=24)

    events = (
        db.query(MitigationLog)
        .filter(MitigationLog.timestamp >= window)
        .all()
    )

    total = len(events)

    protection = sum(
        1 for e in events if e.action == "auto_protection_triggered"
    )

    escalation = sum(
        1 for e in events if e.action == "monitoring_escalated"
    )

    if total == 0:
        trend = "idle"
    elif protection > escalation:
        trend = "aggressive"
    else:
        trend = "watchful"

    return {
        "events_24h": total,
        "protection_actions": protection,
        "monitoring_escalations": escalation,
        "system_posture": trend,
    }
