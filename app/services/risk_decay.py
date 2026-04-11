from datetime import datetime
from sqlalchemy.orm import Session

from app.models.tenant_risk_state import TenantRiskState
from app.services.alert_engine import emit_intelligent_alert
from app.services.event_service import emit_event
from app.services.intelligent_alerts import intelligent_alert
from app.services.policy_runtime import refresh_policy_for_tenant
from app.core.tenant_lock import acquire_tenant_lock


DECAY_RATE = 1  # points per cycle


def decay_risk(db: Session):

    states = db.query(TenantRiskState).all()
    changed = False
    changed_tenant_ids: list[str] = []

    for state in states:
        tenant_state = acquire_tenant_lock(db, state.tenant_id)
        state_changed = False

        if tenant_state.risk_score is None:
            tenant_state.risk_score = 0
            state_changed = True

        old_score = tenant_state.risk_score
        old_level = tenant_state.risk_level
        old_quarantined = tenant_state.quarantined

        # --- decay ---
        tenant_state.risk_score = max(0, tenant_state.risk_score - DECAY_RATE)
        if tenant_state.risk_score != old_score:
            state_changed = True

        # --- recompute level ---
        if tenant_state.risk_score >= 10:
            tenant_state.risk_level = "critical"
        elif tenant_state.risk_score >= 5:
            tenant_state.risk_level = "high"
        elif tenant_state.risk_score >= 2:
            tenant_state.risk_level = "medium"
        else:
            tenant_state.risk_level = "low"
        if tenant_state.risk_level != old_level:
            state_changed = True

        # recovery detection
        if tenant_state.quarantined and tenant_state.risk_level in ("low", "medium"):
            tenant_state.quarantined = False

            intelligent_alert(
                db=db,
                alert_key=f"tenant_recovered_{tenant_state.tenant_id}",
                event_type="tenant_recovered",
                tenant_id=tenant_state.tenant_id,
                payload={"risk_level": tenant_state.risk_level},
            )
        if tenant_state.quarantined != old_quarantined:
            state_changed = True

        if state_changed:
            tenant_state.updated_at = datetime.utcnow()
            changed = True
            changed_tenant_ids.append(tenant_state.tenant_id)

    if changed:
        # Commit is handled at a higher level.
        db.flush()

        for tenant_id in changed_tenant_ids:
            refresh_policy_for_tenant(tenant_id)
