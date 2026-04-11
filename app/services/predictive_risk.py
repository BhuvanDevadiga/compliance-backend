from sqlalchemy.orm import Session
from app.models.system_event import SystemEvent


PREDICTION_WINDOW = 10  # recent events to analyze


def predict_risk(db: Session, tenant_id: str):

    events = (
        db.query(SystemEvent)
        .filter(SystemEvent.tenant_id == tenant_id)
        .order_by(SystemEvent.created_at.desc())
        .limit(PREDICTION_WINDOW)
        .all()
    )

    escalation_signals = 0
    recovery_signals = 0

    for e in events:
        if "escalate" in e.event_type or "quarantine" in e.event_type:
            escalation_signals += 1
        if "recover" in e.event_type:
            recovery_signals += 1

    score = escalation_signals - recovery_signals

    if score >= 5:
        prediction = "imminent_critical_risk"
    elif score >= 2:
        prediction = "risk_building"
    else:
        prediction = "stable"

    return {
        "prediction": prediction,
        "confidence": min(abs(score) * 20, 100),
        "signals_analyzed": len(events),
    }
