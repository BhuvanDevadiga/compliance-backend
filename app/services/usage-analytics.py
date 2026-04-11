from datetime import datetime
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.usage_counter import UsageCounter


def _period_keys(now: datetime):
    return {
        "hour": now.strftime("%Y-%m-%d-%H"),
        "day": now.strftime("%Y-%m-%d"),
        "month": now.strftime("%Y-%m"),
    }


def get_tenant_usage_summary(tenant_id: str):
    now = datetime.utcnow()
    keys = _period_keys(now)

    db = SessionLocal()

    try:
        summary = {}

        for ptype, pkey in keys.items():
            counter = db.execute(
                select(UsageCounter).where(
                    UsageCounter.tenant_id == tenant_id,
                    UsageCounter.period_type == ptype,
                    UsageCounter.period_key == pkey,
                )
            ).scalar_one_or_none()

            summary[ptype] = counter.count if counter else 0

        return summary

    finally:
        db.close()
