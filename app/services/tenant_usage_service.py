from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.tenant_usage import TenantUsage
from app.models.tenant_usage_daily import TenantUsageDaily
from app.services.quota_alerts import maybe_fire_quota_alert
from app.services.abuse_detection import detect_usage_spike

from app.db.database import SessionLocal

db = SessionLocal()

# -------------------------
# EXISTING FUNCTIONS (KEEP)
# -------------------------

def increment_tenant_usage(
    db: Session,
    tenant_id: str,
    path: str,
    method: str,
):
    today = date.today()

    row = (
        db.query(TenantUsage)
        .filter(
            TenantUsage.tenant_id == tenant_id,
            TenantUsage.path == path,
            TenantUsage.method == method,
            TenantUsage.usage_date == today,
        )
        .first()
    )

    if row:
        row.request_count += 1
        row.updated_at = datetime.utcnow()
    else:
        row = TenantUsage(
            tenant_id=tenant_id,
            path=path,
            method=method,
            usage_date=today,
            request_count=1,
        )
        db.add(row)

    db.commit()


def increment_daily_usage(
    db: Session,
    tenant_id: str,
    path: str,
    method: str,
):
    today = date.today()

    row = (
        db.query(TenantUsageDaily)
        .filter_by(
            tenant_id=tenant_id,
            path=path,
            method=method,
            usage_date=today,
        )
        .first()
    )

    if row:
        row.request_count += 1
        row.last_seen = datetime.utcnow()
    else:
        row = TenantUsageDaily(
            tenant_id=tenant_id,
            path=path,
            method=method,
            usage_date=today,
            request_count=1,
        )
        db.add(row)

    db.commit()


def get_today_usage(db: Session, tenant_id: str) -> int:
    today = date.today()

    rows = (
        db.query(TenantUsage.request_count)
        .filter(
            TenantUsage.tenant_id == tenant_id,
            TenantUsage.usage_date == today,
        )
        .all()
    )

    return sum(r[0] for r in rows)


# ----------------------------------
# NEW: SINGLE ENTRY POINT (ADD THIS)
# ----------------------------------

def record_tenant_request(
    db: Session,
    tenant,
    path: str,
    method: str,
):
    """
    Central usage choke-point:
    - increments usage
    - checks quota alerts
    - checks abuse spikes
    """

    # 1️⃣ increment counters
    increment_tenant_usage(db, tenant.tenant_id, path, method)
    increment_daily_usage(db, tenant.tenant_id, path, method)

    # 2️⃣ quota alert (C1)
    used_today = get_today_usage(db, tenant.tenant_id)

    maybe_fire_quota_alert(
        tenant_id=tenant.tenant_id,
        plan=tenant.plan,
        daily_limit=tenant.daily_limit,  # ← TEMP: 2 for testing
        used_today=used_today,
    )

    # 3️⃣ abuse detection (C2) — TEMP baseline
    baseline_per_minute = 2  # ONLY FOR TESTING

    recent_count = used_today  # acceptable for now

    detect_usage_spike(
        tenant_id=tenant.tenant_id,
        recent_count=recent_count,
        baseline_per_minute=baseline_per_minute,
    )
