import random
import statistics
from app.services.health_index import compute_health_index

def simulate_environment(mode="stable", cycles=200):
    results = []

    drift_value = 0.01
    reinforcement = 0.0

    for i in range(cycles):

        # --------------------------
        # Generate synthetic probability
        # --------------------------
        if mode == "stable":
            raw_probability = 0.15 + random.uniform(-0.02, 0.02)

        elif mode == "rising":
            raw_probability = min(1.0, 0.1 + i * 0.003)

        elif mode == "chaotic":
            raw_probability = random.uniform(0.0, 1.0)

        elif mode == "drift_spike":
            raw_probability = 0.2
            if i > cycles // 2:
                drift_value = 0.4

        else:
            raw_probability = 0.2

        # --------------------------
        # Simulate escalation score
        # --------------------------
        escalation_score = 1 if raw_probability > 0.6 else 0

        # --------------------------
        # Hybrid logic
        # --------------------------
        hybrid_score = (0.6 * escalation_score) + (0.4 * raw_probability)

        base_threshold = 0.55
        decision_flag = hybrid_score >= base_threshold

        # --------------------------
        # Health calculation proxy
        # --------------------------
        volatility_score = abs(raw_probability - 0.2)
        confidence = 0.6 * (1 + reinforcement)
        confidence = min(confidence, 1)

        health_index = compute_health_index(
            drift_value,
            volatility_score,
            confidence
        )
        results.append({
            "prob": raw_probability,
            "hybrid": hybrid_score,
            "decision": decision_flag,
            "health": health_index,
        })

    return results