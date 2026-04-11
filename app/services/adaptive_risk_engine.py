from datetime import datetime
from collections import deque
from sqlalchemy.orm import Session

from app.models.tenant_risk_state import TenantRiskState
from app.services.alert_engine import emit_intelligent_alert
from app.services.event_service import emit_event
from app.services.intelligent_alerts import intelligent_alert
from app.services.policy_runtime import refresh_policy_for_tenant
from app.core.tenant_lock import acquire_tenant_lock
from app.services.governance_alert_service import create_alert


RISK_BURST_THRESHOLD_PCT = 50.0
RISK_BURST_WINDOW_SECONDS = 60

_risk_burst_tracker: dict[str, deque[tuple[float, datetime]]] = {}


def check_risk_escalation_burst(db, tenant_id: str, risk_score: float):
    if not tenant_id:
        return

    now = datetime.utcnow()
    window_start = now.timestamp() - RISK_BURST_WINDOW_SECONDS
    events = _risk_burst_tracker.setdefault(tenant_id, deque())

    while events and events[0][1].timestamp() < window_start:
        events.popleft()

    previous_score = events[-1][0] if events else None
    events.append((risk_score, now))

    if previous_score is None:
        return

    if previous_score > 0:
        delta_pct = ((risk_score - previous_score) / previous_score) * 100.0
    else:
        delta_pct = 100.0 if risk_score > 0 else 0.0

    if delta_pct >= RISK_BURST_THRESHOLD_PCT:
        create_alert(
            db=db,
            tenant_id=tenant_id,
            alert_type="risk_escalation_burst",
            severity="high",
            message=(
                "Rapid risk increase detected within short window. "
                "Potential abnormal model behavior or active attack."
            ),
        )


def escalate_risk(db: Session, tenant_id: str, reason: str, severity: int = 1):

    tenant_state = acquire_tenant_lock(db, tenant_id)
    state = tenant_state

    # --- Defensive defaults ---
    if state.risk_score is None:
        state.risk_score = 0

    previous_score = state.risk_score or 0.0
    now = datetime.utcnow()

    # --- Apply escalation ---
    state.risk_score = previous_score + severity

    # --- Risk level logic ---
    if state.risk_score >= 10:
        state.risk_level = "critical"
    elif state.risk_score >= 5:
        state.risk_level = "high"
    elif state.risk_score >= 2:
        state.risk_level = "medium"
    else:
        state.risk_level = "low"

    state.last_escalation_reason = reason
    state.updated_at = now
    state.last_reason = reason

    intelligent_alert(
        db=db,
        alert_key=f"risk_escalated_{tenant_id}",
        event_type="risk_escalated",
        tenant_id=tenant_id,
        payload={"severity": severity},
    )

    if state.risk_level == "critical" and not state.quarantined:
        state.quarantined = True
        state.quarantine_reason = "Auto-quarantined due to critical risk level"
        state.quarantined_at = datetime.utcnow()
        intelligent_alert(
            db=db,
            alert_key=f"tenant_quarantined_{tenant_id}",
            event_type="tenant_quarantined",
            tenant_id=tenant_id,
            payload={"reason": state.quarantine_reason},
        )

    check_risk_escalation_burst(db, tenant_id, state.risk_score)

    # Commit is handled at a higher level.
    db.flush()
    refresh_policy_for_tenant(tenant_id)


def decay_risk(db, tenant_id: str, amount: float = 1.0):
    """
    Reduce tenant risk score gradually (cooldown engine).
    Never drops below zero.
    """

    state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .first()
    )

    if not state:
        return

    # Reduce score safely
    state.risk_score = max(0.0, (state.risk_score or 0) - amount)

    # Recalculate level
    if state.risk_score >= 10:
        state.risk_level = "critical"
    elif state.risk_score >= 5:
        state.risk_level = "high"
    elif state.risk_score >= 2:
        state.risk_level = "medium"
    else:
        state.risk_level = "low"

    state.updated_at = datetime.utcnow()

    if state.risk_level == "critical" and not state.quarantined:

        state.quarantined = True
        state.quarantine_reason = "Auto-quarantined due to critical risk level"
        state.quarantined_at = datetime.utcnow()

        emit_intelligent_alert(
            db=db,
            alert_key=f"tenant_quarantined_{tenant_id}",
            event_type="tenant_quarantined",
            tenant_id=tenant_id,
            payload={"reason": state.quarantine_reason},
        )

    # Commit is handled at a higher level.
    db.flush()
    refresh_policy_for_tenant(tenant_id)
