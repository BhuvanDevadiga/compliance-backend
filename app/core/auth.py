from datetime import datetime
import json

from fastapi import Header, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant import Tenant
from app.models.tenant_api_key import TenantAPIKey
from app.core.security import hash_api_key
from app.services.quota_enforcer import enforce_daily_quota
from app.models.tenant_risk_state import TenantRiskState
from app.services.enforcement_policy import apply_enforcement
from app.services.enforcement_policy import enforce_tenant_policy
from app.services.adaptive_rate_limiter import enforce_rate_limit
from app.core.redis_client import redis_client





CACHE_TTL = 60  # seconds


def get_current_tenant(
    request: Request,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Tenant:
    provided_key = x_api_key
    hashed = hash_api_key(provided_key)

    cache_key = f"api_key:{hashed}"
    cached = redis_client.get(cache_key)
    if cached:
        tenant_data = json.loads(cached)
        tenant = Tenant(
            tenant_id=tenant_data["tenant_id"],
            plan=tenant_data["plan"],
        )
        request.state.tenant = tenant
        return tenant

    key_record = (
        db.query(TenantAPIKey)
        .filter(
            TenantAPIKey.key_hash == hashed,
            TenantAPIKey.is_active == True,
        )
        .first()
    )

    if not key_record:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )
    if key_record.expires_at and key_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key expired")

    key_record.last_used_at = datetime.utcnow()

    tenant = (
        db.query(Tenant)
        .filter(Tenant.tenant_id == key_record.tenant_id)
        .first()
    )

    # 🔒 THIS IS THE QUOTA ENFORCEMENT POINT
    enforce_daily_quota(
        db=db,
        tenant_id=tenant.tenant_id,
    )

    risk_state = (
    db.query(TenantRiskState)
    .filter_by(tenant_id=tenant.tenant_id)
    .first()
    )

    if risk_state:
        apply_enforcement(risk_state.risk_level)

    # Pass risk_state to avoid redundant query
    enforce_tenant_policy(db, tenant.tenant_id, risk_state)
    enforce_rate_limit(db, tenant.tenant_id)

    request.state.tenant = tenant

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(
            {
                "tenant_id": tenant.tenant_id,
                "plan": tenant.plan,
            }
        ),
    )

    return tenant
