from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant import Tenant
from app.services.quota_enforcer import enforce_daily_quota


def get_current_tenant(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = (
        db.query(Tenant)
        .filter(Tenant.api_key == x_api_key)
        .first()
    )

    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    # 🔒 THIS IS THE QUOTA ENFORCEMENT POINT
    enforce_daily_quota(
        db=db,
        tenant_id=tenant.id,
    )

    return tenant
