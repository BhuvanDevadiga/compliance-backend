from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.decision_trace import DecisionTrace
from app.models.mitigation_log import MitigationLog
from app.models.tenant_health import TenantHealthSnapshot
from app.models.tenant_profile import TenantProfile

def get_tenant_intelligence(db: Session, tenant_id: str):

    # --- Last 20 decisions
    traces = (
        db.query(DecisionTrace)
        .filter(DecisionTrace.tenant_id == tenant_id)
        .order_by(desc(DecisionTrace.created_at))
        .limit(20)
        .all()
    )

    recent_decisions = [
        {
            "probability": t.probability,
            "hybrid_score": t.hybrid_score,
            "health_index": t.health_index,
            "accuracy": t.accuracy,
            "pre_mitigation": t.pre_mitigation,
            "final_mitigation": t.final_mitigation,
            "threshold_used": t.threshold_used,
            "timestamp": t.created_at,
            "drift_value": t.drift_value,
            "forecast_state": t.forecast_state,
            "bandit_confidence": t.bandit_confidence,
        }
        for t in traces
    ]

    latest_drift = traces[0].drift_value if traces else None

    if latest_drift is None:
        drift_status = "unknown"
    elif latest_drift < 0.02:
        drift_status = "stable"
    elif latest_drift < 0.05:
        drift_status = "emerging"
    else:
        drift_status = "high_drift"

    latest_forecast_state = traces[0].forecast_state if traces else None
    latest_bandit_confidence = traces[0].bandit_confidence if traces else None

    # --- Health (latest snapshot)
    latest_health = (
        db.query(TenantHealthSnapshot)
        .filter(TenantHealthSnapshot.tenant_id == tenant_id)
        .order_by(desc(TenantHealthSnapshot.created_at))
        .first()
    )
    health_index = latest_health.health_index if latest_health else None

    if health_index >= 0.85:
        health_status = "strong"
    elif health_index >= 0.7:
        health_status = "healthy"
    elif health_index >= 0.6:
        health_status = "caution"
    else:
        health_status = "critical"

    # --- Adaptive Threshold (latest profile/default)
    latest_profile = (
        db.query(TenantProfile)
        .filter(TenantProfile.tenant_id == tenant_id)
        .order_by(desc(TenantProfile.created_at))
        .first()
    )
    adaptive_threshold = (
        latest_profile.adaptive_threshold
        if latest_profile and latest_profile.adaptive_threshold is not None
        else 0.55
    )

    # --- Mitigation Summary
    total_mitigations = (
        db.query(MitigationLog)
        .filter(MitigationLog.tenant_id == tenant_id)
        .count()
    )

    strict_count = (
        db.query(MitigationLog)
        .filter(
            MitigationLog.tenant_id == tenant_id,
            MitigationLog.action == "strict_action",
        )
        .count()
    )

    strict_ratio = (
        strict_count / total_mitigations
        if total_mitigations > 0
        else 0
    )

    if health_status in ["strong", "healthy"] and drift_status == "stable" and strict_ratio < 0.1:
        risk_posture = "stable_low_risk"
    elif drift_status == "emerging" or strict_ratio < 0.2:
        risk_posture = "moderate_watch"
    else:
        risk_posture = "elevated_risk"

    governance_score = round(
        (health_index * 0.5) +
        ((1 - strict_ratio) * 0.3) +
        ((1 - (latest_drift or 0)) * 0.2),
        4
    )    
    return {
        "tenant_id": tenant_id,
        "health_index": health_index,
        "adaptive_threshold": adaptive_threshold,
        "total_mitigations": total_mitigations,
        "strict_actions": strict_count,
        "recent_decisions": recent_decisions,
        "latest_drift": latest_drift,
        "forecast_state": latest_forecast_state,
        "bandit_confidence": latest_bandit_confidence,
        "risk_posture": risk_posture,
        "governance_score": governance_score,
        "total_mitigations": total_mitigations,
        "strict_actions": strict_count,
        "recent_decisions": recent_decisions,
    }
