from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.system_event import SystemEvent
from app.services.risk_trend import analyze_trend

router = APIRouter(
    prefix="/api/admin/trend",
    tags=["Admin Trend"],
)


@router.get("/{tenant_id}")
def tenant_trend(tenant_id: str, db: Session = Depends(get_db)):

    events = (
        db.query(SystemEvent)
        .filter(SystemEvent.tenant_id == tenant_id)
        .order_by(SystemEvent.created_at.desc())
        .limit(20)
        .all()
    )

    events = list(reversed(events))

    return analyze_trend(events)
