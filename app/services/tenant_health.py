def compute_health_score(
    avg_latency: float,
    error_ratio: float,
    risk_level: str,
    quarantined: bool,
) -> dict:
    """
    Compute tenant health score (0–100).
    Higher = healthier.
    """

    score = 100

    # latency penalty
    if avg_latency > 1000:
        score -= 30
    elif avg_latency > 500:
        score -= 15

    # error penalty
    score -= int(error_ratio * 100)

    # risk penalty
    risk_penalties = {
        "low": 0,
        "medium": 10,
        "high": 25,
        "critical": 50,
    }

    score -= risk_penalties.get(risk_level, 0)

    # quarantine penalty
    if quarantined:
        score -= 30

    score = max(0, min(100, score))

    # classification
    if score >= 80:
        status = "healthy"
    elif score >= 50:
        status = "degraded"
    else:
        status = "critical"

    return {
        "health_score": score,
        "status": status,
    }
