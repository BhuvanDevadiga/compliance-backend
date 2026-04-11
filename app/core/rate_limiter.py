import os
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from redis import Redis
from app.core.redis_client import redis_client  # make sure this exists


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
PLAN_CACHE_TTL_SECONDS = 300  # 5 minutes

def api_key_rate_limit_key(request: Request) -> str:
    api_key = request.headers.get("x-api-key")
    if api_key:
        return f"api_key:{api_key}"
    return f"ip:{get_remote_address(request)}"




def get_tenant_plan_from_cache_or_db(api_key: str) -> str:
    

    if not api_key:
        return "free"

    cache_key = f"tenant_plan:{api_key}"

    # Redis is optional/externally hosted; if unavailable, just fallback to DB.
    try:
        cached_plan = redis_client.get(cache_key)
    except Exception:
        cached_plan = None

    if cached_plan is not None:
        if isinstance(cached_plan, bytes):
            return cached_plan.decode()
        return str(cached_plan)

    from app.db.database import SessionLocal
    from app.models.tenant_api_key import TenantAPIKey
    from app.models.tenant import Tenant
    from app.core.security import hash_api_key

    db = SessionLocal()

    try:
        hashed = hash_api_key(api_key)

        key_record = (
            db.query(TenantAPIKey)
            .filter(
                TenantAPIKey.key_hash == hashed,
                TenantAPIKey.is_active == True,
            )
            .first()
        )

        if not key_record:
            plan = "free"
        else:
            tenant = (
                db.query(Tenant)
                .filter(Tenant.tenant_id == key_record.tenant_id)
                .first()
            )
            plan = tenant.plan if tenant else "free"

        plan = plan.lower()

        # 3) Cache in Redis (best-effort, do not fail on Redis downtime).
        try:
            redis_client.setex(cache_key, PLAN_CACHE_TTL_SECONDS, plan)
        except Exception:
            pass

        return plan

    finally:
        db.close()


def tenant_rate_limit(key: str) -> str:
    

    if not key:
        return "10/second"

    api_key = ""
    if key.startswith("api_key:"):
        api_key = key[len("api_key:") :]

    plan = get_tenant_plan_from_cache_or_db(api_key)

    if plan == "pro":
        return "400/second"
    if plan == "enterprise":
        return "1000/second"

    return "10/second"




limiter = Limiter(
    key_func=api_key_rate_limit_key,
    storage_uri=REDIS_URL,
    storage_options={
        "connection_pool": redis_client.connection_pool
    },
)
