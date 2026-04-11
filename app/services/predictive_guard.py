from datetime import datetime
from sqlalchemy.orm import Session

from app.models.tenant_risk_state import TenantRiskState
from app.services.event_bus import emit_event
from app.core.tenant_lock import acquire_tenant_lock


PREDICTIVE_THRESHOLD = 15  # approaching critical
COOLDOWN_BUFFER = 3        # safety margin


def predictive_guard(db: Session):

    states = db.query(TenantRiskState).all()
    changed = False

    for state in states:
        tenant_state = acquire_tenant_lock(db, state.tenant_id)

        if tenant_state.risk_score is None:
            continue

        # approaching danger zone
        if PREDICTIVE_THRESHOLD <= tenant_state.risk_score < 20:

            emit_event(
                event_type="predictive_warning",
                tenant_id=tenant_state.tenant_id,
                payload={
                    "risk_score": tenant_state.risk_score,
                    "message": "Tenant approaching critical risk",
                },
            )

            # soft mitigation — reduce velocity
            tenant_state.risk_score = max(
                PREDICTIVE_THRESHOLD - COOLDOWN_BUFFER,
                tenant_state.risk_score - 2,
            )

            tenant_state.updated_at = datetime.utcnow()
            changed = True

    if changed:
        # Commit is handled at a higher level.
        db.flush()
