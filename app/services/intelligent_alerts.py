from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.alert_state import AlertState
from app.services.event_bus import emit_event


ALERT_COOLDOWN = timedelta(minutes=5)


def intelligent_alert(
    db: Session,
    tenant_id: str,
    alert_key: str,
    event_type: str,
    payload: dict | None = None,
):
    """
    Emits alert with cooldown + deduplication.
    """
    now = datetime.utcnow()
    state = db.query(AlertState).filter_by(alert_key=alert_key).first()

    # Suppress duplicate alert events during cooldown window.
    if state and now - state.last_emitted < ALERT_COOLDOWN:
        return

    emit_event(
        event_type=event_type,
        tenant_id=tenant_id,
        payload=payload or {},
    )

    if not state:
        state = AlertState(alert_key=alert_key)
        db.add(state)

    state.last_emitted = now
    db.commit()
