from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.system_event import SystemEvent

router = APIRouter(prefix="/api/admin/live-events", tags=["Live Events"])


@router.get("/")
def recent_events(db: Session = Depends(get_db)):

    events = (
        db.query(SystemEvent)
        .order_by(SystemEvent.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "event": e.event_type,
            "tenant": e.tenant_id,
            "payload": e.payload,
            "timestamp": e.created_at,
        }
        for e in events
    ]
