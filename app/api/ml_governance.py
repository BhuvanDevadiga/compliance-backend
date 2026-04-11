from fastapi import APIRouter, Depends
from datetime import datetime, timedelta, UTC
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.ml_metadata import MLModelMetadata
from app.models.tenant_drift_log import TenantDriftLog
from app.models.ml_retrain_log import MLModelRetrainLog
from app.db.database import get_db
from app.services.ml_health_service import get_ml_health_report

router = APIRouter(
    prefix = "/api/ml/governance",
    tags = ["ML Governance"],
)

COOLDOWN_HOURS = 6

def classify_drift(drift_value: float) -> str:
    if drift_value < 10:
        return "low"
    elif drift_value < 30:
        return "moderate"
    elif drift_value < 60:
        return "high"
    return "critical"

@router.get("/status")
def get_governance_status(
    db=Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):

    tenant_id = tenant.tenant_id

    metadata = (
        db.query(MLModelMetadata)
        .filter(MLModelMetadata.tenant_id == tenant_id)
        .first()
    )

    if not metadata:
        return {"status": "no_model_metadata"}

    # Latest drift log
    latest_drift = (
        db.query(TenantDriftLog)
        .filter(TenantDriftLog.tenant_id == tenant_id)
        .order_by(TenantDriftLog.created_at.desc())
        .first()
    )

    drift_value = latest_drift.drift_value if latest_drift else 0.0
    drift_severity = classify_drift(drift_value)

    # Cooldown check
    cooldown_active = False
    if metadata.last_retrained_at:
        last_retrained_at = metadata.last_retrained_at
        if last_retrained_at.tzinfo is None:
            last_retrained_at = last_retrained_at.replace(tzinfo=UTC)

        if datetime.now(UTC) - last_retrained_at < timedelta(hours=COOLDOWN_HOURS):
            cooldown_active = True

    # Retrain stats
    retrain_logs = (
        db.query(MLModelRetrainLog)
        .filter(MLModelRetrainLog.tenant_id == tenant_id)
        .order_by(MLModelRetrainLog.created_at.desc())
        .all()
    )

    total_retrains = len(retrain_logs)
    last_retrain_reason = retrain_logs[0].trigger_status if retrain_logs else None
    with db.begin():
        health_report = get_ml_health_report(db)
    ml_health_status = health_report.get("status")

    return {
        "model_version": metadata.model_version,
        "last_retrained_at": metadata.last_retrained_at,
        "cooldown_active": cooldown_active,
        "drift_streak": metadata.drift_streak,
        "latest_drift_value": drift_value,
        "drift_severity": drift_severity,
        "ml_health_status": ml_health_status,
        "confidence_decline_streak": metadata.confidence_decline_streak,
        "total_retrains": total_retrains,
        "last_retrain_reason": last_retrain_reason,
    }

def calculate_drift_trend(drift_logs):
    if len(drift_logs)<2:
        return 0.0
    
    values = [log.drift_value for log in drift_logs]
    x = list(range(len(values)))

    n = len(values)
    mean_x = sum(x) / n
    mean_y = sum(values) / n

    numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

    return numerator / denominator if denominator != 0 else 0.0

@router.get("/history")
def get_governance_history(
    limit: int = 20,
    db=Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    tenant_id = tenant.tenant_id

    # Drift logs
    drift_logs = (
        db.query(TenantDriftLog)
        .filter(TenantDriftLog.tenant_id == tenant_id)
        .order_by(TenantDriftLog.created_at.desc())
        .limit(limit)
        .all()
    )

    drift_logs_sorted = list(reversed(drift_logs))
    drift_trend_slope = calculate_drift_trend(drift_logs_sorted)

    drift_data = [
        {
            "drift_value": log.drift_value,
            "recent_avg": log.recent_avg,
            "baseline_avg": log.baseline_avg,
            "drift_streak": log.drift_streak,
            "model_version": log.model_version,
            "timestamp": log.created_at,
        }
        for log in drift_logs
    ]

    # Retrain logs
    retrain_logs = (
        db.query(MLModelRetrainLog)
        .filter(MLModelRetrainLog.tenant_id == tenant_id)
        .order_by(MLModelRetrainLog.created_at.desc())
        .limit(limit)
        .all()
    )

    retrain_data = [
        {
            "old_version": log.old_version,
            "new_version": log.new_version,
            "trigger_status": log.trigger_status,
            "streak_value": log.streak_value,
            "samples": log.samples,
            "strict_events": log.strict_events,
            "timestamp": log.created_at,
        }
        for log in retrain_logs
    ]

    return {
        "drift_history": drift_data,
        "drift_trend_slope": drift_trend_slope,
        "retrain_history": retrain_data,
        "total_drift_records": len(drift_data),
        "total_retrain_records": len(retrain_data),
    }
