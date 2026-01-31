from datetime import datetime
from sqlalchemy.orm import Session
from app.models.tenant_usage_monthly import TenantUsageMonthly


def increment_monthly_usage(
    db: Session,
    tenant_id: str,
    path: str,
    method: str,
):
    now = datetime.utcnow()

    row = (
        db.query(TenantUsageMonthly)
        .filter_by(
            tenant_id=tenant_id,
            year=now.year,
            month=now.month,
            path=path,
            method=method,
        )
        .first()
    )

    if row:
        row.request_count += 1
        row.last_seen = now
    else:
        row = TenantUsageMonthly(
            tenant_id=tenant_id,
            year=now.year,
            month=now.month,
            path=path,
            method=method,
            request_count=1,
            last_seen=now,
        )
        db.add(row)

    db.commit()
