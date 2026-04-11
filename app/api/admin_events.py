from fastapi import APIRouter, Depends
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.system_event import SystemEvent

router = APIRouter(
    prefix="/api/admin/events",
    tags=["Admin Events"],
)


@router.get("/{tenant_id}")
def tenant_timeline(
    tenant_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):

    events = (
        db.query(SystemEvent)
        .filter(cast(SystemEvent.tenant_id, String) == tenant_id)
        .order_by(SystemEvent.created_at.desc())
        .limit(limit)
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
