from sqlalchemy.orm import Session
from app.models.governance_event_log import GovernanceEventLog
from app.services.governance_alert_service import create_alert

def verify_tenant_chain(db: Session, tenant_id: str) -> bool:
    events = (
        db.query(GovernanceEventLog)
        .filter(GovernanceEventLog.tenant_id == tenant_id)
        .order_by(GovernanceEventLog.id.asc())
        .all()
    )

    previous_hash = "GENESIS"

    for event in events:
        if event.previous_hash != previous_hash:
            create_alert(
                db=db,
                tenant_id=tenant_id,
                alert_type="chain_integrity_break",
                severity="critical",
                message=f"Chain break detected at event_id={event.id}",
            )
            return False
        previous_hash = event.event_hash

    return True
