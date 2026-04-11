
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.request_audit_log import RequestAuditLog
from app.core.auth import get_current_tenant


router = APIRouter(
    prefix="/api/internal/audit",
    tags=["Internal Audit"],
)

@router.get("/trace/{request_id}")
def get_audit_trace(
    request_id: str,
    db: Session = Depends(get_db),
    tenant=Depends(get_current_tenant),
):
    audit = (
        db.query(RequestAuditLog)
        .filter(
            RequestAuditLog.request_id == request_id,
            RequestAuditLog.tenant_id == tenant.tenant_id,  # tenant isolation
        )
        .first()
    )

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit trace not found",
        )

    return {
        "request_id": audit.request_id,
        "tenant_id": audit.tenant_id,
        "path": audit.path,
        "method": audit.method,
        "status_code": audit.status_code,
        "latency_ms": audit.latency_ms,
        "ruleset_version": audit.ruleset_version,
        "ip_address": audit.ip_address,
        "user_agent": audit.user_agent,
        "created_at": audit.created_at,
    }
