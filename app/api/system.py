from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.models.tenant_health import TenantHealthSnapshot
from app.core.auth import get_current_tenant
from app.services.control_risk_service import compute_audit_readiness

router = APIRouter(
    prefix= "/api/system",
    tags = ["System"],
)

@router.get("/tenant/{tenant_id}/health")
def get_tenant_health(tenant_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(TenantHealthSnapshot)
        .filter(TenantHealthSnapshot.tenant_id == tenant_id)
        .order_by(desc(TenantHealthSnapshot.created_at))
        .first()
    )

    if not row:
        return {"message": "No health data available"}

    return {
        "tenant_id": tenant_id,
        "health_index": row.health_index,
        "drift_value": row.drift_value,
        "confidence_score": row.confidence_score,
        "volatility_score": row.volatility_score,
        "timestamp": row.created_at,
    }


@router.get("/tenant/{tenant_id}/audit-readiness")
def get_audit_readiness(tenant_id: str, db: Session = Depends(get_db)):
    readiness = compute_audit_readiness(db, tenant_id)

    return {
        "tenant_id": tenant_id,
        "audit_readiness_score": readiness,
        "percentage": round(readiness * 100, 2)
    }
