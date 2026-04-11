from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.models.usage_counter import UsageCounter


def _period_keys(now: datetime):
    return {
        "hour": now.strftime("%Y-%m-%d-%H"),
        "day": now.strftime("%Y-%m-%d"),
        "month": now.strftime("%Y-%m"),
    }


def increment_usage(tenant_id: str):
    now = datetime.utcnow()
    periods = _period_keys(now)

    db = SessionLocal()

    try:
        for ptype, pkey in periods.items():

            counter = db.execute(
                select(UsageCounter).where(
                    UsageCounter.tenant_id == tenant_id,
                    UsageCounter.period_type == ptype,
                    UsageCounter.period_key == pkey,
                )
            ).scalar_one_or_none()

            if counter:
                counter.count += 1
            else:
                counter = UsageCounter(
                    tenant_id=tenant_id,
                    period_type=ptype,
                    period_key=pkey,
                    count=1,
                )
                db.add(counter)

            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                counter = db.execute(
                    select(UsageCounter).where(
                        UsageCounter.tenant_id == tenant_id,
                        UsageCounter.period_type == ptype,
                        UsageCounter.period_key == pkey,
                    )
                ).scalar_one()

                counter.count += 1
                db.commit()

    finally:
        db.close()
