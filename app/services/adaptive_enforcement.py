from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.tenant_risk_state import TenantRiskState
from app.services.event_service import emit_event


def enforce_tenant_policy(db: Session, tenant_id: str, state: TenantRiskState = None):
    """
    Reads tenant adaptive risk state and applies enforcement logic.
    If state is provided, use it; otherwise query the database.
    """

    if not state:
        state = (
            db.query(TenantRiskState)
            .filter(TenantRiskState.tenant_id == tenant_id)
            .first()
        )

    if not state:
        return  # no enforcement needed

    level = state.risk_level

    # --- CRITICAL: deny access ---
    if level == "critical":
        emit_event(
            event_type="tenant_blocked",
            tenant_id=tenant_id,
            payload={"risk_score": state.risk_score},
        )

        raise HTTPException(
            status_code=429,
            detail="Tenant temporarily blocked due to risk escalation",
        )

    # --- HIGH: heavy throttling signal ---
    if level == "high":
        emit_event(
            event_type="tenant_high_risk",
            tenant_id=tenant_id,
            payload={"risk_score": state.risk_score},
        )

    # --- MEDIUM: soft throttle signal ---
    if level == "medium":
        emit_event(
            event_type="tenant_soft_throttle",
            tenant_id=tenant_id,
            payload={"risk_score": state.risk_score},
        )
