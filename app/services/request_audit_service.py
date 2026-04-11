from sqlalchemy.orm import Session
from app.models.request_audit_log import RequestAuditLog


def write_request_audit_log(
    db: Session,
    *,
    request_id: str,
    tenant_id: str | None,
    path: str,
    method: str,
    status_code: int,
    latency_ms: int,
    payload_hash: str | None,
    ruleset_version: str | None,
):
    log = RequestAuditLog(
        request_id=request_id,
        tenant_id=tenant_id,
        path=path,
        method=method,
        status_code=status_code,
        latency_ms=latency_ms,
        payload_hash=payload_hash,
        ruleset_version=ruleset_version,
    )

    db.add(log)
    db.commit()
