from sqlalchemy.orm import Session
from app.models.request_audit_log import RequestAuditLog
from app.models.system_event import SystemEvent


def get_tenant_timeline(db: Session, tenant_id: str, limit: int = 50):
    audit_logs = (
        db.query(RequestAuditLog)
        .filter(RequestAuditLog.tenant_id == tenant_id)
        .all()
    )

    events = (
        db.query(SystemEvent)
        .filter(SystemEvent.tenant_id == tenant_id)
        .all()
    )

    timeline = []

    for a in audit_logs:
        timeline.append({
            "type": "request",
            "timestamp": a.created_at,
            "data": {
                "path": a.path,
                "method": a.method,
                "status": a.status_code,
                "latency": a.latency_ms,
            },
        })

    for e in events:
        timeline.append({
            "type": "event",
            "timestamp": e.created_at,
            "data": {
                "event_type": e.event_type,
                "payload": e.payload,
            },
        })

    timeline.sort(key=lambda x: x["timestamp"], reverse=True)

    return timeline[:limit]
