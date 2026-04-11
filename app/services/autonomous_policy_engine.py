from sqlalchemy.orm import Session
from app.services.mitigation_learning import evaluate_mitigation_effectiveness
from app.services.behavior_escalation_engine import evaluate_behavior_escalation

def autonomous_policy_adjustment(db: Session, tenant_id: str):
    """
    Core engine that evaluates tenant behavior and determines
    if mitigation or escalation is needed.
    """

    effectiveness = evaluate_mitigation_effectiveness(db, tenant_id)
    escalation = evaluate_behavior_escalation(db, tenant_id)

    adjustment_score = 0

    # escalation pressure
    if escalation["escalation"]:
        adjustment_score += 1

    # mitigation learning signal
    if effectiveness["learning"] == "failure":
        adjustment_score += 1
    elif effectiveness["learning"] == "mild_success":
        adjustment_score += 0
    elif effectiveness["learning"] == "strong_success":
        adjustment_score -= 1

    # decision mapping
    if adjustment_score >= 2:
        policy = "tighten_controls"
    elif adjustment_score <= -1:
        policy = "relax_controls"
    else:
        policy = "maintain"

    return {
        "tenant_id": tenant_id,
        "policy_adjustment": policy,
        "adjustment_score": adjustment_score,
        "signals": {
            "escalation": escalation,
            "effectiveness": effectiveness,
        },
    }


# Backward-compatible alias for existing imports.
def autonomus_policy_engine(db: Session, tenant_id: str):
    return autonomous_policy_adjustment(db, tenant_id)


