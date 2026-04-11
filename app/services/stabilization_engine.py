from datetime import datetime
from sqlalchemy.orm import Session

from app.models.tenant_risk_state import TenantRiskState
from app.services.event_bus import emit_event
from app.core.tenant_lock import acquire_tenant_lock


def stabilize_tenants(db: Session):

    states = db.query(TenantRiskState).all()
    changed = False

    for state in states:
        tenant_state = acquire_tenant_lock(db, state.tenant_id)

        # Only act on quarantined tenants
        if not tenant_state.quarantined:
            continue

        # Behavioral stabilization rules
        if tenant_state.risk_level == "medium":
            tenant_state.quarantined = False

            emit_event(
                event_type="tenant_stabilized",
                tenant_id=tenant_state.tenant_id,
                payload={"risk_level": tenant_state.risk_level},
            )

            tenant_state.updated_at = datetime.utcnow()
            changed = True

        elif tenant_state.risk_level == "low":
            tenant_state.quarantined = False

            emit_event(
                event_type="tenant_released",
                tenant_id=tenant_state.tenant_id,
                payload={"risk_level": tenant_state.risk_level},
            )

            tenant_state.updated_at = datetime.utcnow()
            changed = True

    if changed:
        # Commit is handled at a higher level.
        db.flush()
