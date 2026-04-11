from sqlalchemy.orm import Session
from statistics import mean
from collections import Counter
from app.models.autonomous_decision_log import AutonomousDecisionLog
from app.services.adaptive_thresholds import compute_dynamic_thresholds

def compute_system_state(db: Session, tenant_id: str, window:int = 50):
    decisions=(
        db.query(AutonomousDecisionLog)
        .filter(AutonomousDecisionLog.tenant_id==tenant_id)
        .order_by(AutonomousDecisionLog.created_at.desc())
        .limit(window)
        .all()

    )
    if not decisions:
        return {
            "risk_posture": "no_data",
            "avg_probability": 0,
            "forecast_reliability": 0,
            "escalation_rate": 0,
            "current_mitigation_bias": None,
            "system_confidence": "low",
        }
    
    probabilities = [d.final_probability for d in decisions if d.final_probability is not None]
    accuracies = [d.forecast_accuracy for d in decisions if d.forecast_accuracy is not None]
    escalations = [d.escalation_score for d in decisions if d.escalation_score is not None]
    mitigations = [d.mitigation_level for d in decisions if d.mitigation_level]

    avg_probability = round(mean(probabilities), 3) if probabilities else 0
    forecast_reliability = round(mean(accuracies), 3) if accuracies else 0
    escalation_rate = round(sum(1 for e in escalations if e > 0) / len(escalations), 3) if escalations else 0

    mitigation_bias = None
    if mitigations:
        mitigation_bias = Counter(mitigations).most_common(1)[0][0]

    watch_threshold, critical_threshold = compute_dynamic_thresholds(forecast_reliability,escalation_rate,)

    if avg_probability >= critical_threshold:
        posture = "critical"
    elif avg_probability >= watch_threshold:
        posture = "watch"
    else:
        posture = "stable"

    if forecast_reliability >= 0.85:
        confidence = "high"
    elif forecast_reliability >= 0.6:
        confidence = "medium"
    else:
        confidence = "low"
        
    return {
        "risk_posture": posture,
        "avg_probability": avg_probability,
        "forecast_reliability": forecast_reliability,
        "escalation_rate": escalation_rate,
        "current_mitigation_bias": mitigation_bias,
        "system_confidence": confidence,
        "watch_threshold": watch_threshold,
        "critical_threshold": critical_threshold,
    }    