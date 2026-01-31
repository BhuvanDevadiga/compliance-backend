from datetime import date
from fastapi import APIRouter, Depends

from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.analytics import EndpointUsage
from app.services.usage_analytics import get_tenant_usage_summary

router = APIRouter(
    prefix="/api/internal/analytics",
    tags=["Analytics"],
)


@router.get(
    "/usage",
    response_model=list[EndpointUsage],
)
def tenant_usage_analytics(
    start_date: date | None = None,
    end_date: date | None = None,
    tenant: Tenant = Depends(get_current_tenant),
):
    return get_tenant_usage_summary(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
    )
