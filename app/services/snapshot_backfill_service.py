from sqlalchemy.orm import Session
from app.models.mitigation_log import MitigationLog
from app.models.training_snapshot import TrainingSnapshot
from app.ml.features import build_feature_vector

ESCALATION_ACTIONS = ["strict_action"]   


def backfill_training_snapshots(db: Session):

    logs = db.query(MitigationLog).all()

    created = 0

    for log in logs:
        features = build_feature_vector(db, log.tenant_id)

        escalated = 1 if log.action in ESCALATION_ACTIONS else 0

        snapshot = TrainingSnapshot(
            tenant_id=log.tenant_id,
            **features,
            escalated=escalated
        )

        db.add(snapshot)
        created += 1

    db.commit()

    return {
        "total_logs": len(logs),
        "snapshots_created": created
    }
