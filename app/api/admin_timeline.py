from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.system_event import SystemEvent

router = APIRouter(
    prefix="/api/admin/timeline",
    tags=["Admin Timeline"],
)


@router.get("/{tenant_id}")
def tenant_timeline(tenant_id: str, db: Session = Depends(get_db)):

    events = (
        db.query(SystemEvent)
        .filter(SystemEvent.tenant_id == tenant_id)
        .order_by(SystemEvent.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "event": e.event_type,
            "payload": e.payload,
            "timestamp": e.created_at,
        }
        for e in events
    ]
