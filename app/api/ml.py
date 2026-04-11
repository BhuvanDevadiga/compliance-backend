from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.ml_health_service import get_health_report
from app.models.ml_metadata import MLModelMetadata
from app.models.ml_retrain_log import MLModelRetrainLog
from app.core.auth import get_current_tenant
from sqlalchemy import or_

router = APIRouter(
    prefix="/api/ml",
    tags=["ML Observability"]
)
@router.get("/health")
def ml_health(db: Session = Depends(get_db)):
    with db.begin():
        return get_health_report(db)

@router.get("/version")
def ml_version(
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant)
):
    metadata = db.query(MLModelMetadata).filter(
        or_(
            MLModelMetadata.tenant_id == tenant.tenant_id,
            MLModelMetadata.tenant_id.is_(None),
        )
    ).order_by(
        MLModelMetadata.tenant_id.is_(None)
    ).first()

    if not metadata:
        return {"model_version": None}

    return {
        "model_version": metadata.model_version,
        "last_retrained_at": metadata.last_retrained_at,
        "confidence_decline_streak": metadata.confidence_decline_streak
    } 

@router.get("/retrain/history")
def retrain_history(db: Session = Depends(get_db)):
    logs = db.query(MLModelRetrainLog).order_by(
        MLModelRetrainLog.created_at.desc()
    ).all()

    return [
        {
            "old_version": l.old_version,
            "new_version": l.new_version,
            "trigger_status": l.trigger_status,
            "streak_value": l.streak_value,
            "samples": l.samples,
            "strict_events": l.strict_events,
            "created_at": l.created_at
        }
        for l in logs
    ]
