from sqlalchemy.orm import Session
from app.models.tenant_system_state import TenantSystemState
from datetime import datetime


def get_tenant_state(db: Session, tenant_id: str) -> TenantSystemState:
    state = db.query(TenantSystemState).filter_by(tenant_id=tenant_id).first()

    if not state:
        state = TenantSystemState(
            tenant_id=tenant_id,
            adaptive_engine_frozen=False
        )
        db.add(state)
        # Commit is handled at a higher level.
        db.flush()
        db.refresh(state)

    return state
