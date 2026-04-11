from datetime import date
from sqlalchemy import func

from app.db.database import SessionLocal
from app.models.request_audit_log import RequestAuditLog



def get_tenant_usage_summary(
    tenant_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
):
    db = SessionLocal()
    try:
        query = (
            db.query(
                RequestAuditLog.path.label("path"),
                func.count().label("request_count"),
                func.avg(RequestAuditLog.response_time_ms).label("avg_latency_ms"),
            )
            .filter(RequestAuditLog.tenant_id == tenant_id)
        )

        if start_date:
            query = query.filter(RequestAuditLog.created_at >= start_date)

        if end_date:
            query = query.filter(RequestAuditLog.created_at <= end_date)

        query = query.group_by(RequestAuditLog.path)

        return query.all()
    finally:
        db.close()
