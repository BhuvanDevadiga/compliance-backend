from app.models.ml_metadata import MLModelMetadata
from app.models.mitigation_log import MitigationLog
from app.services.ml_evaluation_service import evaluate_ml_performance
from sqlalchemy import func
import numpy as np


def update_confidence_decline_streak(metadata, current_status, db):
    if current_status == "confidence_declining":
        metadata.confidence_decline_streak = (metadata.confidence_decline_streak or 0) + 1
    else:
        metadata.confidence_decline_streak = 0

    # Commit is handled at a higher level.
    db.flush()


def get_ml_health_report(db):

    metadata = db.query(MLModelMetadata).first()
    if not metadata:
        metadata = MLModelMetadata()
        db.add(metadata)
        # Commit is handled at a higher level.
        db.flush()

    metrics = evaluate_ml_performance(db)

    samples = db.query(MitigationLog)\
        .filter(MitigationLog.ml_probability != None)\
        .count()
    
    avg_confidence = db.query(func.avg(MitigationLog.confidence))\
        .filter(MitigationLog.confidence != None)\
        .scalar()
    
    recent_confidences = db.query(MitigationLog.confidence)\
        .filter(MitigationLog.confidence != None)\
        .order_by(MitigationLog.timestamp.desc())\
        .limit(20)\
        .all()
    recent_confidences = [c[0] for c in reversed(recent_confidences)]

    confidence_trend_slope = None

    if len(recent_confidences) >= 5:
        x = np.arange(len(recent_confidences))
        y = np.array(recent_confidences)

        slope = np.polyfit(x, y, 1)[0]
        confidence_trend_slope = float(slope)

    low_confidence_count = db.query(func.count(MitigationLog.id))\
        .filter(MitigationLog.confidence != None)\
        .filter(MitigationLog.confidence < 0.3)\
        .scalar()
    
    low_confidence_ratio = None
    if samples and samples > 0:
        low_confidence_ratio = low_confidence_count / samples

    strict_events = db.query(MitigationLog)\
        .filter(MitigationLog.actual_escalated == 1)\
        .count()

    report = {
        "model_version": metadata.model_version if metadata else 1,
        "samples": samples,
        "strict_events": strict_events,
        "precision": metrics.get("precision"),
        "recall": metrics.get("recall"),
        "f1_score": metrics.get("f1_score"),
        "last_retrained_at": str(metadata.last_retrained_at) if metadata else None,
        "status": "healthy",
        "avg_confidence": float(avg_confidence) if avg_confidence is not None else None,
        "low_confidence_count": low_confidence_count,
        "low_confidence_ratio": low_confidence_ratio,
        "confidence_trend_slope": confidence_trend_slope,
    }

    if samples < 20:
        report["status"] = "insufficient_data"

    elif metrics.get("f1_score") is not None and metrics["f1_score"] < 0.6:
        report["status"] = "degrading"

    elif (
        samples >= 20
        and confidence_trend_slope is not None
        and confidence_trend_slope < -0.02
    ):
        report["status"] = "confidence_declining"    

    elif low_confidence_ratio is not None and low_confidence_ratio > 0.4:
        report["status"] = "uncertainty_rising" 

    update_confidence_decline_streak(metadata, report["status"], db)

    return report


def get_health_report(db):
    return get_ml_health_report(db)


