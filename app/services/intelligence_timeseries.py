from sqlalchemy.orm import Session
from app.models.decision_trace import DecisionTrace

STRICT_ACTIONS = {
    "strict_action",
    "block",
    "rate_limit",
    "quarantine",

}


def _normalize_action(action: str) -> str:
    if not action:
        return ""
    return action.strip().lower()

def build_timeseries(db: Session, tenant_id:str, limit:int=100):
    traces = (
        db.query(DecisionTrace)
        .filter(DecisionTrace.tenant_id == tenant_id)
        .order_by(DecisionTrace.created_at.desc())
        .limit(limit)
        .all()
    )

    traces = list(reversed(traces))

    health_trend = []
    drift_trend = []
    governance_trend = []
    strict_ratio_trend = []

    strict_count = 0
    total_count = 0

    for t in traces:

        ts = t.created_at.isoformat()

        health_trend.append({
            "timestamp": ts,
            "value": t.health_index or 0
        })

        drift_trend.append({
            "timestamp": ts,
            "value": t.drift_value or 0
        })

        total_count += 1
        if _normalize_action(t.final_mitigation) in STRICT_ACTIONS:
            strict_count += 1

        strict_ratio = strict_count / total_count if total_count else 0

        drift_value = t.drift_value or 0
        health_value = t.health_index or 0
        governance_score = round(
            (health_value * 0.5)
            + ((1 - strict_ratio) * 0.3)
            + ((1 - drift_value) * 0.2),
            4,
        )

        governance_trend.append({
            "timestamp": ts,
            "value": governance_score
        })

        strict_ratio_trend.append({
            "timestamp": ts,
            "value": strict_ratio
        })

    return {
        "health_index_trend": health_trend,
        "drift_trend": drift_trend,
        "governance_trend": governance_trend,
        "strict_ratio_trend": strict_ratio_trend,
    }
