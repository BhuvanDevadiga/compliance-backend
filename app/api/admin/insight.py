from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant_risk_state import TenantRiskState
from app.services.risk_insight import generate_risk_insight

router = APIRouter(
    prefix="/api/admin/insight",
    tags=["Admin Insight"],
)


@router.get("/{tenant_id}")
def tenant_insight(tenant_id: str, db: Session = Depends(get_db)):

    state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .first()
    )

    if not state:
        raise HTTPException(404, "Tenant not found")

    return generate_risk_insight(state)
