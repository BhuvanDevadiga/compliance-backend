from statistics import pstdev

from sqlalchemy.orm import Session

from app.models.system_event import SystemEvent


INTELLIGENCE_WINDOW = 50


def compute_risk_intelligence(db: Session, tenant_id: str):
    events = (
        db.query(SystemEvent)
        .filter(SystemEvent.tenant_id == tenant_id)
        .order_by(SystemEvent.created_at.desc())
        .limit(INTELLIGENCE_WINDOW)
        .all()
    )

    if not events:
        return {
            "behavior_score": 0,
            "volatility": "unknown",
            "classification": "no history",
        }

    escalation_events = [e for e in events if "escalat" in e.event_type]
    signal_density = len(escalation_events) / len(events)

    pattern_values = [1 if "escalat" in e.event_type else 0 for e in events]
    volatility_score = pstdev(pattern_values) if len(pattern_values) > 1 else 0

    if volatility_score > 0.45:
        volatility = "chaotic"
    elif volatility_score > 0.2:
        volatility = "unstable"
    else:
        volatility = "stable"

    if signal_density > 0.5:
        classification = "high-risk behavior"
    elif signal_density > 0.25:
        classification = "elevated behavior"
    else:
        classification = "normal behavior"

    return {
        "behavior_score": round(signal_density, 3),
        "volatility": volatility,
        "classification": classification,
    }
