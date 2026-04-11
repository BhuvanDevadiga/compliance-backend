from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.mitigation_log import MitigationLog

def did_escalate_recently(db: Session, tenant_id: str, window_hours: int = 24):
    cutoff_time = datetime.utcnow()  - timedelta(hours=window_hours)

    escalation = (
        db.query(MitigationLog)
        .filter(
            MitigationLog.tenant_id == tenant_id,
            MitigationLog.timestamp >= cutoff_time,
            MitigationLog.action.in_(["AGGRESSIVE", "HARD_BLOCK"])
        )
        .first()

    )
    return escalation is not None
