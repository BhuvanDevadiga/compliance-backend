import random

from app.models.mitigation_strategy import MitigationStrategy
from app.services.mitigation_feedback_engine import select_best_mitigation
from app.models.tenant_profile import TenantProfile
from app.services.risk_forecasting import predict_risk_horizon

EPSILON = 0.05


def auto_route_mitigation(db, tenant_id, base_probability, override_strategy=None):
    probability = float(base_probability)

    profile = db.query(TenantProfile).filter(
        TenantProfile.tenant_id == tenant_id
    ).first()

    base_threshold = profile.adaptive_threshold if profile else 0.55

    forecast = predict_risk_horizon(db, tenant_id, horizon=5)
    adaptive_threshold = (
        profile.adaptive_threshold
        if profile and profile.adaptive_threshold is not None
        else base_threshold
    )
    print("[FORECAST PEAK]", forecast["expected_peak"])
    print("[ADAPTIVE THRESHOLD USED]", adaptive_threshold)

    if forecast["expected_peak"] >= adaptive_threshold:
        print("[PROACTIVE ESCALATION TRIGGERED]")
        probability = max(probability, forecast["expected_peak"])
    aggressive_threshold = adaptive_threshold + 0.2
    active_threshold = adaptive_threshold - 0.1    


    if probability >= aggressive_threshold:
        level = "aggressive"
    elif probability >= active_threshold:
        level = "active"
    else:
        level = "advisory"

    if override_strategy:
        return {
            "probability": probability,
            "level": level,
            "recommended_mitigation": override_strategy,
            "confidence": 1.0,
        }

    strategies = select_best_mitigation(db, tenant_id, level)
    if isinstance(strategies, str):
        candidate_strategies = [strategies]
    else:
        candidate_strategies = list(strategies or [])

    if not candidate_strategies:
        return {
            "probability": probability,
            "level": level,
            "recommended_mitigation": None,
            "confidence": 0,
        }

    if random.random() < EPSILON:
        chosen = random.choice(candidate_strategies)
        return {
            "probability": probability,
            "level": level,
            "recommended_mitigation": chosen,
            "confidence": 0.5,
        }

    # EXPLOIT: choose highest average_reward
    best_strategy = candidate_strategies[0]
    best_confidence = 0.5
    best_reward = -999
    print("LEVEL:", level)
    print("CANDIDATES:", candidate_strategies)

    for strategy in candidate_strategies:
        record = (
            db.query(MitigationStrategy)
            .filter(
                MitigationStrategy.tenant_id == tenant_id,
                MitigationStrategy.strategy == strategy,
            )
            .first()
        )
        print("STRATEGY:", strategy, "REWARD:", record.average_reward if record else None)

        avg_reward = record.average_reward if record else 0

        if avg_reward > best_reward:
            best_reward = avg_reward
            best_strategy = strategy
            best_confidence = avg_reward  # optional mapping

    return {
    "probability": probability,
    "level": level,
    "recommended_mitigation": best_strategy,
    "confidence": round(best_confidence, 3),
}
