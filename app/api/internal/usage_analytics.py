from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.db.database import get_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.services.usage_analytics_service import (
    get_tenant_usage_summary,
    get_tenant_endpoint_breakdown,
)

router = APIRouter(
    prefix="/api/internal/usage",
    tags=["Internal Analytics"],
)


@router.get("/summary", operation_id="internal_usage_summary_v1")
def tenant_usage_summary(
    day: date | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return get_tenant_usage_summary(
        db=db,
        tenant_id=tenant.tenant_id,
        day=day,
    )


@router.get("/endpoints", operation_id="internal_endpoint_usage_v1")
def tenant_endpoint_usage(
    day: date | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return get_tenant_endpoint_breakdown(
        db=db,
        tenant_id=tenant.tenant_id,
        day=day,
    )
