from sqlalchemy.orm import Session
from app.models.decision_trace import DecisionTrace
from app.services.incident_engine import create_incident

STRICT_ACTIONS = {
    "strict_action",
    "strictaction",
    "strict-action",
    "strict action",
    "block",
    "rate_limit",
    "rate-limit",
    "rate limit",
    "quarantine",
}


def _normalize_action(action: str) -> str:
    if not action:
        return ""
    return action.strip().lower()

def analyze_tenant_pulse(db:Session, tenant_id:str, limit:int=50):
    traces=(
        db.query(DecisionTrace)
        .filter(DecisionTrace.tenant_id == tenant_id)
        .order_by(DecisionTrace.created_at.desc())
        .limit(limit)
        .all()
    )

    if len(traces)<2:
        return{
            "pulse":"insufficient_data",
            "health_delta": 0,
            "drift_detected":False,
            "strict_ratio": 0,
            "governance_delta":0
        }
    
    latest=traces[0]
    earliest=traces[-1]

    health_delta = (latest.health_index or 0) - (earliest.health_index or 0)
    drift_detected = any((t.drift_value or 0) > 0 for t in traces)

    strict_count = sum(
        1 for t in traces if _normalize_action(t.final_mitigation) in STRICT_ACTIONS
    )
    strict_ratio = strict_count / len(traces)

    latest_governance = round(
        ((latest.health_index or 0) * 0.5)
        + ((1 - strict_ratio) * 0.3)
        + ((1 - (latest.drift_value or 0)) * 0.2),
        4,
    )
    earliest_governance = round(
        ((earliest.health_index or 0) * 0.5)
        + ((1 - strict_ratio) * 0.3)
        + ((1 - (earliest.drift_value or 0)) * 0.2),
        4,
    )
    governance_delta = latest_governance - earliest_governance

    signals = []

    if health_delta < -0.05:
        signals.append("risk_spike")

    if drift_detected:
        signals.append("drift_alert")

    if strict_ratio > 0.4:
        signals.append("mitigation_overuse")

    if governance_delta < -0.05:
        signals.append("governance_drop")

    if not signals:
        signals.append("stable")

    for signal in signals:
        if signal != "stable":
            create_incident(
            db,
            tenant_id,
            signal,
            health_delta,
            strict_ratio,
            governance_delta
        )    

    return {
        "signals": signals,
        "health_delta": health_delta,
        "drift_detected": drift_detected,
        "strict_ratio": strict_ratio,
        "governance_delta": governance_delta
    }
    
