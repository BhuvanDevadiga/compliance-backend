from sqlalchemy.orm import Session
from app.models.escalation_feedback import EscalationFeedback

def learn_adaptive_threshold(db: Session, tenant_id: str, window: int = 20):
    """
    Placeholder for learning logic to adjust escalation thresholds.

    In a real implementation, this would analyze historical feedback
    and outcomes to refine the threshold computation.
    """
    history = (
        db.query(EscalationFeedback)
        .filter(EscalationFeedback.tenant_id == tenant_id)
        .order_by(EscalationFeedback.timestamp.desc())
        .limit(window)
        .all()
    )

    if len(history) < 5:
        return 3
    
    escalation_rate = sum(
        1 for h in history if h.escalation_triggered
    ) / len(history)

    if escalation_rate > 0.7:
        return 5
    
    if escalation_rate < 0.3:
        return 2
    
    return 3