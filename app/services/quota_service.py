# app/core/quota/service.py
from datetime import date
from sqlalchemy.orm import Session
from app.models.tenant_quota import TenantQuota
from app.models.tenant_usage_daily import TenantUsageDaily
from app.core.quota.alerts import maybe_fire_quota_alert
from sqlalchemy import func

def get_quota_snapshot(db: Session, tenant_id: str):
    quota = (
        db.query(TenantQuota)
        .filter(TenantQuota.tenant_id == tenant_id)
        .first()
    )

    used = (
        db.query(func.coalesce(func.sum(TenantUsageDaily.request_count), 0))
        .filter(
            TenantUsageDaily.tenant_id == tenant_id,
            TenantUsageDaily.usage_date == date.today(),
        )
        .scalar()
    )

    plan = quota.plan if quota else "free"
    daily_limit = quota.daily_limit if quota else None

    if daily_limit is not None and daily_limit > 0:
        maybe_fire_quota_alert(
            tenant_id=tenant_id,
            plan=plan,
            daily_limit=daily_limit,
            used_today=used,
        )

    return {
        "plan": plan,
        "daily_limit": daily_limit,
        "used": used,
        "remaining": (max(daily_limit - used, 0) if daily_limit else None),
    }
