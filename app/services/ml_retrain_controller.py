from datetime import UTC, datetime, timedelta
from sqlalchemy.orm import Session
from app.models.mitigation_log import MitigationLog
from app.services.ml_evaluation_service import evaluate_ml_performance
from app.services.ml_health_service import get_health_report
from app.services.ml_trainer_service import train_escalation_model
from app.models.ml_retrain_log import MLModelRetrainLog
from sqlalchemy import desc
from app.models.risk_history import RiskHistory
from app.models.tenant_drift_log import TenantDriftLog
from app.models.ml_metadata import MLModelMetadata

MIN_SAMPLES = 20
MIN_STRICT_EVENTS = 5
COOLDOWN_HOURS = 24


def controlled_retrain_if_needed(db: Session, tenant_id: str):
    health = get_health_report(db)
    status = health.get("status")

    metrics = evaluate_ml_performance(db)
    if "f1_score" not in metrics:
        return {"status": "not_ready"}

    samples = metrics["samples"]
    strict_count = (
        db.query(MitigationLog)
        .filter(MitigationLog.actual_escalated == 1)
        .count()
    )

    if samples < MIN_SAMPLES:
        return {"status": "insufficient_samples"}
    if strict_count < MIN_STRICT_EVENTS:
        return {"status": "insufficient_strict_events"}

    metadata = db.query(MLModelMetadata).filter(MLModelMetadata.tenant_id == tenant_id).first()
    if not metadata:
        metadata = MLModelMetadata(
            tenant_id=tenant_id,
            model_version=1,
            confidence_decline_streak=0,
            drift_streak=0 
        )
        db.add(metadata)
        # Commit is handled at a higher level.
        db.flush()
        db.refresh(metadata)

    recent_scores = (
        db.query(RiskHistory)
        .filter(RiskHistory.tenant_id == tenant_id)
        .order_by(desc(RiskHistory.created_at))
        .limit(50)
        .all()
    )

    baseline_scores = (
        db.query(RiskHistory)
        .filter(RiskHistory.tenant_id == tenant_id)
        .order_by(desc(RiskHistory.created_at))
        .offset(50)
        .limit(200)
        .all()
    )

    recent_scores = [r.probability for r in recent_scores]
    baseline_scores = [r.probability for r in baseline_scores]

    DRIFT_THRESHOLD = 0.15
    drift_value = 0
    recent_avg = None
    baseline_avg = None

    if len(recent_scores) >= 20 and len(baseline_scores) >= 50:
        recent_avg = sum(recent_scores) / len(recent_scores)
        baseline_avg = sum(baseline_scores) / len(baseline_scores)

        drift_value = abs(recent_avg - baseline_avg)
        print("Recent avg:", recent_avg)
        print("Baseline avg:", baseline_avg)
        print("Drift value:", drift_value)
        print("Old streak:", metadata.drift_streak) 

        if drift_value > DRIFT_THRESHOLD:
            metadata.drift_streak += 1
        else:
            metadata.drift_streak = 0

        print("New streak:", metadata.drift_streak)    
    
    

    model_meta =(
        db.query(MLModelMetadata)
        .filter(MLModelMetadata.tenant_id == tenant_id)
        .first()
    )    

    log_entry = TenantDriftLog(
        tenant_id=tenant_id,
        recent_avg=recent_avg,
        baseline_avg=baseline_avg,
        drift_value=drift_value,
        drift_streak=metadata.drift_streak,
        model_version=model_meta.model_version if model_meta else None,
    )
    db.add(log_entry)
    # Commit is handled at a higher level.
    db.flush()
    

    # Decide retrain
    should_retrain = False
    trigger_type = None

    if status in ["degrading", "uncertainty_rising"]:
        should_retrain = True
        trigger_type = "low_confidence"

    elif status == "confidence_declining" and metadata.confidence_decline_streak >= 3:
        should_retrain = True
        trigger_type = "low_confidence"

    elif metadata.drift_streak >= 2:
        should_retrain = True
        trigger_type = "drift"

    if not should_retrain:
        
        return {"status": "no_retrain_needed"}

    # Cooldown check
    if metadata.last_retrained_at:
        last_retrained_at = metadata.last_retrained_at
        if last_retrained_at.tzinfo is None:
            last_retrained_at = last_retrained_at.replace(tzinfo=UTC)

        if datetime.now(UTC) - last_retrained_at < timedelta(hours=COOLDOWN_HOURS):
            return {"status": "cooldown_active"}

    # Retrain
    train_escalation_model(db)

    old_version = metadata.model_version or 0
    
    streak_value = (
    metadata.drift_streak
    if trigger_type == "drift"
    else metadata.confidence_decline_streak
    )

    log = MLModelRetrainLog(
        tenant_id=tenant_id,
        old_version=old_version,
        new_version=old_version + 1,
        trigger_status=trigger_type,
        streak_value=streak_value,
        samples=samples,
        strict_events=strict_count,
    )
    db.add(log)

    metadata.confidence_decline_streak = 0
    metadata.drift_streak = 0

    def classify_drift(drift_value: float) -> str:

        if drift_value < 10:
            return "low"
        elif drift_value < 30:
            return "moderate"
        elif drift_value < 60:
            return "high"
        return "critical"

    metadata.model_version = (metadata.model_version or 0) + 1
    metadata.last_retrained_at = datetime.now(UTC)
    metadata.confidence_decline_streak = 0
    metadata.drift_streak = 0  # IMPORTANT reset after retrain
    # Commit is handled at a higher level.
    db.flush()

    return {"status": "retrained", "new_version": metadata.model_version, "trigger_type": trigger_type}
