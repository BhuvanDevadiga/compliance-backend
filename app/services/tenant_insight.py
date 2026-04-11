from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.request_audit_log import RequestAuditLog
from app.models.tenant_risk_state import TenantRiskState
from app.services.tenant_health import compute_health_score
from app.services.tenant_alerts import evaluate_alerts




def get_tenant_insight(db: Session, tenant_id: str):

    # ---------------------------
    # Traffic statistics
    # ---------------------------

    total_requests = (
        db.query(func.count(RequestAuditLog.id))
        .filter(RequestAuditLog.tenant_id == tenant_id)
        .scalar()
    ) or 0

    avg_latency = (
        db.query(func.avg(RequestAuditLog.latency_ms))
        .filter(RequestAuditLog.tenant_id == tenant_id)
        .scalar()
    ) or 0

    error_count = (
        db.query(func.count(RequestAuditLog.id))
        .filter(
            RequestAuditLog.tenant_id == tenant_id,
            RequestAuditLog.status_code >= 500,
        )
        .scalar()
    ) or 0

    error_ratio = (error_count / total_requests) if total_requests else 0

    # ---------------------------
    # Risk snapshot
    # ---------------------------

    state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .first()
    )

    risk_snapshot = {
        "risk_score": state.risk_score if state else 0,
        "risk_level": state.risk_level if state else "unknown",
        "quarantined": state.quarantined if state else False,
    }

    # ---------------------------
    # Behavioral insights
    # ---------------------------

    insights = []

    if avg_latency > 800:
        insights.append("High latency trend detected")

    if error_ratio > 0.1:
        insights.append("Elevated server error rate")

    if state and state.quarantined:
        insights.append("Tenant currently isolated due to risk escalation")

    if not insights:
        insights.append("Tenant operating within normal parameters")

    # ---------------------------
    # Final intelligence payload
    # ---------------------------
    health = compute_health_score(
        avg_latency=avg_latency,
        error_ratio=error_ratio,
        risk_level=risk_snapshot["risk_level"],
        quarantined=risk_snapshot["quarantined"],
    )
    
    evaluate_alerts(
        tenant_id=tenant_id,
        health_score=health["health_score"],
        risk_level=risk_snapshot["risk_level"],
        quarantined=risk_snapshot["quarantined"],
    )

    return {
        "tenant": tenant_id,
        "traffic": {
            "total_requests": total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "error_count": error_count,
            "error_ratio": round(error_ratio, 3),
        },
        "risk": risk_snapshot,
        "health": health,
        "insights": insights,
    }
