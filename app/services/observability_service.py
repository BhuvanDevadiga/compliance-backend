
from app.models.request_audit_log import RequestAuditLog
from app.db.database import SessionLocal




def write_audit_log(db, event: dict):
    latency = event.get("latency_ms")

    audit = RequestAuditLog(
        tenant_id=event.get("tenant_id"),
        method=event.get("method"),
        path=event.get("path"),
        status_code=event.get("status_code"),

        
        response_time_ms=latency,
        correlation_id=event.get("request_id"),

        ruleset_version=event.get("ruleset_version"),
       
        request_id=event.get("request_id"),
        api_key_hash=event.get("api_key_hash"),
        latency_ms=latency,
        ip_address=event.get("ip_address"),
        user_agent=event.get("user_agent"),
        request_hash=event.get("request_hash"),
        response_size=event.get("response_size"),
    )

    db.add(audit)
    db.commit()

def get_audit_trace(request_id: str):
    db = SessionLocal()
    try:
        record = (
            db.query(RequestAuditLog)
            .filter(RequestAuditLog.request_id == request_id)
            .first()
        )

        if not record:
            return None

        return {
            "request_id": record.request_id,
            "tenant_id": record.tenant_id,
            "method": record.method,
            "path": record.path,
            "status_code": record.status_code,
            "latency_ms": record.latency_ms,
            "ruleset_version": record.ruleset_version,
            "ip_address": record.ip_address,
            "user_agent": record.user_agent,
            "created_at": record.created_at,
        }

    finally:
        db.close()


