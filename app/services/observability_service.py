from app.models import audit_log
from app.models.audit_log import RequestAuditLog



def write_audit_log(db, event: dict):
    latency = event.get("latency_ms")

    audit = RequestAuditLog(
        tenant_id=event.get("tenant_id"),
        method=event.get("method"),
        path=event.get("path"),
        status_code=event.get("status_code"),

        
        response_time_ms=latency,
        correlation_id=event.get("request_id"),

       
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




