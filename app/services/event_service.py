from app.db.database import SessionLocal
from app.models.system_event import SystemEvent
from app.services.alert_dispatcher import dispatch_alert
import threading


def _emit_event_sync(
    event_type: str,
    payload: dict,
    tenant_id: str | None = None,
    severity: str = "info",
):
    """Internal synchronous event emission"""
    db = SessionLocal()

    try:
        event = SystemEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            severity=severity,
            payload=payload,
        )

        db.add(event)
        db.commit()

        critical_events = {
            "risk_escalated",
            "anomaly_request_spike",
            "anomaly_error_burst",
            "tenant_quarantined",
        }

        if event_type in critical_events:
            dispatch_alert(event_type, tenant_id, payload or {})

    except Exception:
        db.rollback()
    finally:
        db.close()


def emit_event(
    event_type: str,
    payload: dict,
    tenant_id: str | None = None,
    severity: str = "info",
):
    """
    Emit event asynchronously to avoid blocking the request.
    Uses background thread for non-critical events.
    """
    thread = threading.Thread(
        target=_emit_event_sync,
        args=(event_type, payload, tenant_id, severity),
        daemon=True,
    )
    thread.start()
