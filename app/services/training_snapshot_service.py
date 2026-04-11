from sqlalchemy.orm import Session
from app.models.training_snapshot import TrainingSnapshot
from app.ml.features import build_feature_vector
from app.services.escalation_tracker import did_escalate_recently

def create_training_snapshot(db: Session, tenant_id: str):
    features = build_feature_vector(db, tenant_id)

    escalated = 1 if did_escalate_recently(db, tenant_id) else 0

    snapshot = TrainingSnapshot(
        tenant_id=tenant_id,
        **features,
        escalated=escalated
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "tenant_id": tenant_id,
        "snapshot_id": snapshot.id,
        "escalated": escalated
    }