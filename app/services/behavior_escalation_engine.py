from sqlalchemy.orm import Session
from app.models.behavior_memory import BehaviorMemory
from app.services.adaptive_escalation import compute_adaptive_threshold
from app.models.escalation_feedback import EscalationFeedback
from app.services.escalation_learning_engine import learn_adaptive_threshold
from app.services.mitigation_learning import evaluate_mitigation_effectiveness






def evaluate_behavior_escalation(
    db: Session,
    tenant_id: str,
    window: int = 5,
):
    """
    Escalation engine with adaptive threshold learning.

    Looks at recent behavior history and decides
    whether escalation should trigger.
    """

    history = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(window)
        .all()
    )

    threshold = compute_adaptive_threshold(db, tenant_id)
    learning = evaluate_mitigation_effectiveness(db, tenant_id)

    if len(history) < window:
        return {
            "escalation": False,
            "critical_events": sum(1 for h in history if h.classification == "critical behavior"),
            "adaptive_threshold": threshold,
            "window": window,
            "reason": "insufficient history",
        }

    critical_count = sum(
        1 for h in history if h.classification == "critical behavior"
    )

    escalation_triggered = critical_count >= threshold
    feedback_payload = {
        "tenant_id": tenant_id,
        "escalation_triggered": escalation_triggered,
        "adaptive_threshold": threshold,
    }
    db.add(EscalationFeedback(**feedback_payload))
    # Commit is handled at a higher level.
    db.flush()

    return {
        "escalation": escalation_triggered,
        "critical_events": critical_count,
        "adaptive_threshold": threshold,
        "window": window,
        "learning_feedback": learning,
    }
