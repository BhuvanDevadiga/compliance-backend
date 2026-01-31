from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.tenant_usage_daily import TenantUsageDaily


def get_usage_today(db: Session, tenant_id: str):
    today = date.today()

    return (
        db.query(
            TenantUsageDaily.path,
            TenantUsageDaily.method,
            TenantUsageDaily.request_count,
            TenantUsageDaily.last_seen,
        )
        .filter(
            TenantUsageDaily.tenant_id == tenant_id,
            TenantUsageDaily.usage_date == today,
        )
        .all()
    )


def get_usage_last_n_days(db: Session, tenant_id: str, days: int):
    start_date = date.today() - timedelta(days=days)

    rows = (
        db.query(TenantUsageDaily)
        .filter(
            TenantUsageDaily.tenant_id == tenant_id,
            TenantUsageDaily.usage_date >= start_date,
        )
        .all()
    )

    aggregated = {}

    for r in rows:
        key = (r.path, r.method)
        if key not in aggregated:
            aggregated[key] = {
                "path": r.path,
                "method": r.method,
                "request_count": 0,
                "last_seen": r.last_seen,
            }

        aggregated[key]["request_count"] += r.request_count

        if r.last_seen and (
            aggregated[key]["last_seen"] is None
            or r.last_seen > aggregated[key]["last_seen"]
        ):
            aggregated[key]["last_seen"] = r.last_seen

    return list(aggregated.values())
