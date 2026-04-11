from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant_risk_state import TenantRiskState
from app.models.tenant_profile import TenantProfile
from app.models.request_audit_log import RequestAuditLog

router = APIRouter(
    prefix="/api/admin/overview",
    tags=["Admin Overview"],
)


@router.get("/{tenant_id}")
def tenant_overview(tenant_id: str, db: Session = Depends(get_db)):

    risk = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .first()
    )

    profile = (
        db.query(TenantProfile)
        .filter(TenantProfile.tenant_id == tenant_id)
        .first()
    )

    recent_requests = (
        db.query(RequestAuditLog)
        .filter(RequestAuditLog.tenant_id == tenant_id)
        .count()
    )

    if not risk:
        raise HTTPException(404, "Tenant not found")

    return {
        "tenant": tenant_id,

        "risk": {
            "score": risk.risk_score,
            "level": risk.risk_level,
            "quarantined": risk.quarantined,
            "last_reason": risk.last_escalation_reason,
            "updated": risk.updated_at,
        },

        "profile": {
            "avg_latency": getattr(profile, "avg_latency_ms", None),
            "request_rate": getattr(profile, "request_rate", None),
            "error_ratio": getattr(profile, "error_ratio", None),
            "endpoint_distribution": getattr(profile, "endpoint_distribution", {}),
        },

        "activity": {
            "total_audit_events": recent_requests
        },
    }
