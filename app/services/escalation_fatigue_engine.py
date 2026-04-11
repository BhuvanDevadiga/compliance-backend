from sqlalchemy.orm import Session
from app.models.escalation_feedback import EscalationFeedback

def detect_escalation_fatigue(db: Session, tenant_id: str, window: int = 10, fatigue_threshold: float = 0.8):
    """
    Detects potential escalation fatigue by analyzing recent escalation feedback.

    If a high rate of escalations is observed without corresponding improvements,
    this may indicate fatigue and the need for threshold adjustments.
    """

    history = (

        db.query(EscalationFeedback)
        .filter(EscalationFeedback.tenant_id == tenant_id)
        .order_by(EscalationFeedback.timestamp.desc())
        .limit(window)
        .all()
    )

    if len(history) < window:
        return {
            "fatigue_detected": False,
            "escalation_rate": None,
            "reason": "insufficient feedback history",
        }
    
    escalation_rate = sum(1 for h in history if h.escalation_triggered) / len(history)

    fatugue_detected = escalation_rate >= fatigue_threshold

    return {
        "fatigue_detected": fatugue_detected,   
        "escalation_rate": escalation_rate,
        "window": window,
    }