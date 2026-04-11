from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.mitigation_log import MitigationLog

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/mitigation/history/{tenant_id}")
def mitigation_history(tenant_id: str, db: Session = Depends(get_db)):

    logs = (
        db.query(MitigationLog)
        .filter(MitigationLog.tenant_id == tenant_id)
        .order_by(MitigationLog.timestamp.desc())
        .all()
    )

    return [
        {
            "action": log.action,
            "prediction": log.prediction,
            "context": log.context,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]
