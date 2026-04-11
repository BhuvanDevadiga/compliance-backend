from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant_risk_state import TenantRiskState

router = APIRouter(
    prefix="/api/admin/risk",
    tags=["Admin Risk"],
)


@router.get("/{tenant_id}")
def get_tenant_risk(tenant_id: str, db: Session = Depends(get_db)):

    state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .first()
    )

    if not state:
        raise HTTPException(404, "Tenant risk state not found")

    return {
        "tenant_id": state.tenant_id,
        "risk_score": state.risk_score,
        "risk_level": state.risk_level,
        "quarantined": state.quarantined,
        "last_reason": state.last_escalation_reason,
        "updated_at": state.updated_at,
    }


@router.post("/{tenant_id}/reset")
def reset_risk(tenant_id: str, db: Session = Depends(get_db)):

    with db.begin():
        state = (
            db.query(TenantRiskState)
            .filter(TenantRiskState.tenant_id == tenant_id)
            .first()
        )

        if not state:
            raise HTTPException(404, "Tenant risk state not found")

        state.risk_score = 0
        state.risk_level = "low"
        state.quarantined = False
        state.last_escalation_reason = None

    return {"status": "risk reset complete"}


@router.post("/{tenant_id}/release")
def release_quarantine(tenant_id: str, db: Session = Depends(get_db)):

    with db.begin():
        state = (
            db.query(TenantRiskState)
            .filter(TenantRiskState.tenant_id == tenant_id)
            .first()
        )

        if not state:
            raise HTTPException(404, "Tenant risk state not found")

        state.quarantined = False

    return {"status": "tenant released"}
