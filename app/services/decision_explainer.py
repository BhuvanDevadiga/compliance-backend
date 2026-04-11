from sqlalchemy.orm import Session
from app.models.decision_trace import DecisionTrace


def _clamp_probability(value: float | None, default: float = 0.5) -> float:
    if value is None:
        return default
    return round(min(max(value, 0.0), 1.0), 4)


def explain_decision(db: Session, decision_id: int):

    decision = (
        db.query(DecisionTrace)
        .filter(DecisionTrace.id == decision_id)
        .first()
    )

    if not decision:
        return {"error": "Decision not found"}

    hybrid_score = getattr(decision, "hybrid_score", None)
    threshold = (
        getattr(decision, "adaptive_threshold", None)
        if hasattr(decision, "adaptive_threshold")
        else getattr(decision, "threshold_used", None)
    )
    ml_probability = (
        getattr(decision, "ml_probability", None)
        if hasattr(decision, "ml_probability")
        else getattr(decision, "probability", None)
    )
    mitigation_action = (
        getattr(decision, "mitigation_action", None)
        if hasattr(decision, "mitigation_action")
        else getattr(decision, "final_mitigation", None)
    )
    timestamp = (
        getattr(decision, "timestamp", None)
        if hasattr(decision, "timestamp")
        else getattr(decision, "created_at", None)
    )
    rule_score = getattr(decision, "rule_score", None)
    if (
        rule_score is None
        and hybrid_score is not None
        and ml_probability is not None
    ):
        # hybrid = 0.6 * rule + 0.4 * ml  ->  rule = (hybrid - 0.4 * ml) / 0.6
        rule_score = (hybrid_score - (0.4 * ml_probability)) / 0.6

    bandit_confidence = getattr(decision, "bandit_confidence", None)

    if hybrid_score is not None and threshold is not None and hybrid_score >= threshold:
        reason = "hybrid score exceeded adaptive threshold"
    elif hybrid_score is not None and threshold is not None:
        reason = "score below threshold but mitigation applied via bandit strategy"
    else:
        reason = "insufficient trace fields to compute threshold comparison"

    return {
        "decision_id": decision.id,
        "tenant_id": decision.tenant_id,
        "timestamp": timestamp,
        "rule_score": _clamp_probability(rule_score, default=0.0),
        "ml_probability": _clamp_probability(ml_probability, default=0.0),
        "hybrid_score": _clamp_probability(hybrid_score, default=0.0),
        "adaptive_threshold": _clamp_probability(threshold, default=0.55),
        "mitigation_action": mitigation_action,
        "bandit_confidence": _clamp_probability(bandit_confidence, default=0.5),
        "reason": reason
    }
