from fastapi import APIRouter, Depends
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.db.database import get_db
from app.services.risk_forecast import forecast_risk

router = APIRouter(
    prefix = "/api/ml/predict",
    tags=["ML Predictive Intelligence"],
)

@router.get("/forecast")
def get_risk_forecast(
    db=Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    result = forecast_risk(db, tenant.tenant_id)
    return result

