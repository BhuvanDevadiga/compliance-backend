import time
from collections import defaultdict
from datetime import datetime, timedelta

from app.models.tenant_risk_state import TenantRiskState
from app.models.tenant import Tenant
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


# in-memory counters (demo-safe)
request_buckets = defaultdict(list)


PLAN_CAPACITY_PER_MINUTE = {
    "free": 10 * 60,
    "pro": 400 * 60,
    "enterprise": 1000 * 60,
}

RISK_SCALE = {
    "low": 1.0,
    "medium": 0.5,
    "high": 0.25,
    "critical": 0.0,
}


WINDOW = timedelta(minutes=1)


def enforce_rate_limit(db, tenant_id: str):
    state = (
        db.query(TenantRiskState)
        .filter_by(tenant_id=tenant_id)
        .first()
    )

    tenant = (
        db.query(Tenant)
        .filter_by(tenant_id=tenant_id)
        .first()
    )

    plan = (tenant.plan.lower() if tenant and tenant.plan else "free")
    if plan not in PLAN_CAPACITY_PER_MINUTE:
        plan = "free"

    risk = (state.risk_level if state else "low")
    if risk not in RISK_SCALE:
        risk = "low"

    base_capacity = PLAN_CAPACITY_PER_MINUTE[plan]
    allowed_requests = int(base_capacity * RISK_SCALE[risk])

    now = datetime.utcnow()
    bucket = request_buckets[tenant_id]

    # remove expired timestamps
    request_buckets[tenant_id] = [
        t for t in bucket if now - t < WINDOW
    ]

    bucket = request_buckets[tenant_id]

    if allowed_requests <= 0:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Tenant blocked by adaptive limiter",
        )

    if len(bucket) >= allowed_requests:
        time.sleep(1)  # soft throttle
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Tenant rate limited",
        )

    bucket.append(now)
