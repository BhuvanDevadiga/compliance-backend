from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.system_event import SystemEvent


def emit_event(
    event_type: str,
    tenant_id: str | None = None,
    payload: dict | None = None,
):
    db: Session = SessionLocal()

    try:
        event = SystemEvent(
            event_type=event_type,
            tenant_id=tenant_id,
            payload=payload or {},
        )

        db.add(event)
        db.commit()

    finally:
        db.close()
