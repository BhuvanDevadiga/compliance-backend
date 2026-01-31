import time
import uuid
from fastapi import Request, Response

from app.db.database import SessionLocal
from app.models.audit_log import RequestAuditLog
from app.models.tenant import Tenant


def log_request_audit(
    *,
    request: Request,
    response: Response,
    tenant: Tenant,
    start_time: float,
) -> None:
    db = SessionLocal()
    try:
        elapsed_ms = int((time.time() - start_time) * 1000)

        audit = RequestAuditLog(
            tenant_id=tenant.id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time_ms=elapsed_ms,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            correlation_id=str(uuid.uuid4()),
        )

        db.add(audit)
        db.commit()
    finally:
        db.close()
