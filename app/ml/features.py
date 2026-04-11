from sqlalchemy.orm import Session
from app.models.tenant_behavior_profile import TenantBehaviorProfile
from app.models.mitigation_strategy_performance import MitigationStrategyPerformance
from app.services.predictive_guard_engine import predictive_escalation_guard
from app.services.risk_forecasting import predict_risk_horizon, get_forecast_accuracy

def build_feature_vector(db: Session, tenant_id: str) -> dict:
    """
    Centralized ML feature builder.
    All ML models MUST consume features only from here.
    """

    # -----------------------------
    # 1️⃣ Behavior Layer
    # -----------------------------
    profile = db.query(TenantBehaviorProfile).filter_by(
        tenant_id=tenant_id
    ).first()

    if not profile:
        return {}

    velocity_data = predictive_escalation_guard(db, tenant_id)

    velocity = velocity_data.get("velocity", 0.0)
    stability = profile.stability_score or 0.5
    bias = profile.escalation_bias or 0.0

    # -----------------------------
    # 2️⃣ Forecast Layer
    # -----------------------------
    forecast = predict_risk_horizon(db, tenant_id, horizon=5)

    forecast_peak = forecast.get("expected_peak", 0.0)
    forecast_accuracy = get_forecast_accuracy(db, tenant_id) or 0.5

    # -----------------------------
    # 3️⃣ Adaptive Threshold
    # -----------------------------
    volatility = 1 - stability
    adaptive_threshold = 0.55 + (stability * 0.1) - (volatility * 0.1) - (bias * 0.05)
    adaptive_threshold = max(0.3, min(0.8, adaptive_threshold))

    # -----------------------------
    # 4️⃣ Strategy Performance (Aggregate)
    # -----------------------------
    strategy_rows = db.query(MitigationStrategyPerformance).filter(
        MitigationStrategyPerformance.tenant_id == tenant_id
    ).all()

    if strategy_rows:
        avg_confidence = sum(
            r.confidence or 0 for r in strategy_rows
        ) / len(strategy_rows)

        avg_success_ratio = sum(
            (r.success_score or 0) /
            ((r.success_score or 0) + (r.failure_score or 0) or 1)
            for r in strategy_rows
        ) / len(strategy_rows)

        short_term_ratio = sum(
            (r.short_term_success or 0) /
            ((r.short_term_success or 0) + (r.short_term_failure or 0) or 1)
            for r in strategy_rows
        ) / len(strategy_rows)
    else:
        avg_confidence = 0.5
        avg_success_ratio = 0.5
        short_term_ratio = 0.5

    # -----------------------------
    # 5️⃣ Final Feature Vector
    # -----------------------------
    features = {
        "velocity": velocity,
        "stability": stability,
        "bias": bias,
        "forecast_peak": forecast_peak,
        "forecast_accuracy": forecast_accuracy,
        "adaptive_threshold": adaptive_threshold,
        "volatility": volatility,
        "avg_strategy_confidence": avg_confidence,
        "long_term_success_ratio": avg_success_ratio,
        "short_term_success_ratio": short_term_ratio,
    }

    return features

