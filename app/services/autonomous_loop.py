from sqlalchemy.orm import Session
from app.services.behavior_escalation_engine import evaluate_behavior_escalation
from app.services.mitigation_learning import evaluate_mitigation_effectiveness
from app.services.autonomous_policy_engine import autonomous_policy_adjustment
from app.services.predictive_guard_engine import predictive_escalation_guard


def run_autonomous_feedback_cycle(
        db: Session,
        tenant_id: str,
):
    escalation = evaluate_behavior_escalation(db, tenant_id)
    effectiveness = evaluate_mitigation_effectiveness(db, tenant_id)
    policy = autonomous_policy_adjustment(db, tenant_id)
    guard = predictive_escalation_guard(db, tenant_id)


    return {
        "tenant": tenant_id,
        "cycle": {
            "escalation": escalation,
            "effectiveness": effectiveness,
            "policy_adjustment": policy,
            "predictive_guard": guard,
        },
    }
   
