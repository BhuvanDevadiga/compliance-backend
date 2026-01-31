from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models.audit_log import RequestAuditLog


def get_tenant_usage_summary(
    db: Session,
    tenant_id: int,
    day: date | None = None,
):
    """
    Returns total request count and avg latency for a tenant.
    """

    query = db.query(
        func.count(RequestAuditLog.id).label("request_count"),
        func.avg(RequestAuditLog.response_time_ms).label("avg_latency_ms"),
    ).filter(
        RequestAuditLog.tenant_id == tenant_id
    )

    if day:
        query = query.filter(
            func.date(RequestAuditLog.created_at) == day
        )

    result = query.one()

    return {
        "tenant_id": tenant_id,
        "request_count": result.request_count or 0,
        "avg_latency_ms": int(result.avg_latency_ms or 0),
    }


def get_tenant_endpoint_breakdown(
    db: Session,
    tenant_id: int,
    day: date | None = None,
):
    """
    Returns request counts grouped by method + path.
    """

    query = db.query(
        RequestAuditLog.method,
        RequestAuditLog.path,
        func.count(RequestAuditLog.id).label("count"),
    ).filter(
        RequestAuditLog.tenant_id == tenant_id
    )

    if day:
        query = query.filter(
            func.date(RequestAuditLog.created_at) == day
        )

    query = query.group_by(
        RequestAuditLog.method,
        RequestAuditLog.path,
    ).order_by(func.count(RequestAuditLog.id).desc())

    rows = query.all()

    return [
        {
            "method": r.method,
            "path": r.path,
            "count": r.count,
        }
        for r in rows
    ]
