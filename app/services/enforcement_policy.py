import time
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tenant_risk_state import TenantRiskState

def apply_enforcement(risk_level: str):
    """
    Adaptive enforcement based on tenant risk level.
    """

    if risk_level == "low":
        return

    if risk_level == "medium":
        # soft degradation
        time.sleep(0.2)

    elif risk_level == "high":
        # aggressive slowdown
        time.sleep(1.0)

    elif risk_level == "critical":
        raise HTTPException(
            status_code=429,
            detail="Tenant temporarily isolated due to critical risk",
        )
def enforce_tenant_policy(db: Session, tenant_id: str, state: TenantRiskState = None):
    """
    DB-driven enforcement wrapper.
    If state is provided, use it; otherwise query the database.
    """

    if not state:
        state = (
            db.query(TenantRiskState)
            .filter(TenantRiskState.tenant_id == tenant_id)
            .first()
        )

    if not state:
        return
    
    if state.quarantined:
        raise HTTPException(
            status_code=429,
            detail="Tenant temporarily blocked (quarantined)",
        )
    apply_enforcement(state.risk_level)