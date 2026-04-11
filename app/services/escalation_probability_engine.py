import logging

from sqlalchemy.orm import Session

from app.core.config import USE_ML_MODEL
from app.ml.hybrid_predictor import predict_probability as compute_hybrid_score
from app.models.tenant_behavior_profile import TenantBehaviorProfile
from app.models.tenant_drift_log import TenantDriftLog
from app.services.ml_inference_service import compute_ml_score
from app.services.predictive_guard_engine import predictive_escalation_guard

logger = logging.getLogger("app.escalation_engine")

def compute_escalation_probability(db: Session, tenant_id: str, source: str = "default"):

    guard = predictive_escalation_guard(db, tenant_id)
    latest_drift = (
        db.query(TenantDriftLog)
        .filter(TenantDriftLog.tenant_id == tenant_id)
        .order_by(TenantDriftLog.created_at.desc())
        .first()
    )
    drift = latest_drift.drift_value if latest_drift else 0.0

    profile = db.query(TenantBehaviorProfile).filter_by(
        tenant_id=tenant_id
    ).first()

    if not profile:
        return {
            "probability": 0.2,
            "reason": "No behavior profile found",
            "drift": drift,
        }

    velocity = guard.get("velocity", 0)
    stability = profile.stability_score
    bias = profile.escalation_bias

    try:
        heuristic_score = compute_hybrid_score(db, tenant_id)
        ml_score = compute_ml_score(db, tenant_id)
        selected_score = ml_score if USE_ML_MODEL else heuristic_score

        logger.info(
            "escalation_score_comparison",
            extra={
                "tenant_id": tenant_id,
                "heuristic_score": round(heuristic_score, 4),
                "ml_score": round(ml_score, 4),
                "selected_score": round(selected_score, 4),
                "model_active": USE_ML_MODEL,
            },
        )

        probability = selected_score
    except Exception as e:
        logger.warning(
            "escalation_score_fallback",
            extra={"tenant_id": tenant_id, "source": source, "error": str(e)},
        )

        probability = (
            0.4 * max(0, velocity)
            + 0.3 * (1 - stability)
            + 0.3 * max(0, bias / 3)
        )

    probability = min(1.0, max(0.0, probability))

    return {
        "probability": round(probability, 3),
        "velocity": velocity,
        "stability": stability,
        "bias": bias,
        "drift": drift,
    }
