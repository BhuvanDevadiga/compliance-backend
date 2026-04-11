from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.alert_state import AlertState
from app.services.event_service import emit_event

ALERT_COOLDOWN = timedelta(minutes=5)


def emit_intelligent_alert(
    db: Session,
    alert_key: str,
    event_type: str,
    tenant_id: str,
    payload: dict,
):
    state = db.query(AlertState).filter_by(alert_key=alert_key).first()

    now = datetime.utcnow()

    if state and now - state.last_emitted < ALERT_COOLDOWN:
        return  # suppress duplicate alert

    if not state:
        state = AlertState(alert_key=alert_key)
        db.add(state)

    state.last_emitted = now

    emit_event(event_type, tenant_id, payload)

    db.commit()
