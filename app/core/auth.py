from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant import Tenant

def get_current_tenant(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    tenant = (
        db.query(Tenant)
        .filter(
            Tenant.tenant_id == x_tenant_id,
            Tenant.api_key == x_api_key,
            Tenant.is_active == True,
        )
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=401,
            detail="Invalid tenant or API key",
        )

    return tenant
