from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.tenant_intelligence_service import get_tenant_intelligence
from app.schemas.intelligence_timeseries import TenantTimeseriesResponse
from app.schemas.intelligence_pulse import TenantPulseResponse
from app.services.intelligence_timeseries import build_timeseries
from app.services.intelligence_pulse import analyze_tenant_pulse
from app.models.compliance_incident import ComplianceIncident
from app.services.tenant_risk_engine import compute_tenant_risk


router = APIRouter(prefix="/api/tenant", tags=["Tenant Intelligence"])

@router.get("/intelligence/{tenant_id}")
def tenant_intelligence(tenant_id: str, db: Session = Depends(get_db)):
    return get_tenant_intelligence(db, tenant_id)

@router.get(
    "/api/tenant/intelligence/{tenant_id}/timeseries",
    response_model=TenantTimeseriesResponse
)
def tenant_timeseries(
    tenant_id: str,
    db: Session = Depends(get_db)
):

    trends = build_timeseries(db, tenant_id)

    return {
        "tenant_id": tenant_id,
        **trends
    }

@router.get(
    "/intelligence/{tenant_id}/pulse",
    response_model=TenantPulseResponse
)
def tenant_pulse(
    tenant_id: str,
    db: Session = Depends(get_db)
):

    pulse_data = analyze_tenant_pulse(db, tenant_id)

    return {
        "tenant_id": tenant_id,
        **pulse_data
    }

@router.get("/intelligence/{tenant_id}/incidents")
def tenant_incidents(tenant_id: str, db: Session = Depends(get_db)):

    incidents = (
        db.query(ComplianceIncident)
        .filter(ComplianceIncident.tenant_id == tenant_id)
        .order_by(ComplianceIncident.detected_at.desc())
        .limit(50)
        .all()
    )

    return incidents

@router.get("/risk/{tenant_id}")
def tenant_risk(tenant_id: str, db: Session = Depends(get_db)):
    return compute_tenant_risk(db, tenant_id)