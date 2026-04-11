from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.tenant_risk_state import TenantRiskState


def enforce_risk_policy(db: Session, tenant_id: str, state: TenantRiskState = None):
    """
    Applies enforcement rules based on tenant risk level.
    If state is provided, use it; otherwise query the database.
    """

    if not state:
        state = (
            db.query(TenantRiskState)
            .filter(TenantRiskState.tenant_id == tenant_id)
            .first()
        )

    if not state:
        return  # no restrictions

    level = state.risk_level

    # --- CRITICAL → block ---
    if level == "critical":
        raise HTTPException(
            status_code=403,
            detail="Tenant temporarily blocked due to risk escalation",
        )

    # --- HIGH → throttle ---
    if level == "high":
        raise HTTPException(
            status_code=429,
            detail="Tenant temporarily throttled due to high risk",
        )

    # medium / low → allowed
