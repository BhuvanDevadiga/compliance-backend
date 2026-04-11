from app.services.volatility import compute_volatility

def compute_health_index(drift_value, volatility_score, confidence_score):
    drift_value = min(max(drift_value, 0), 1)
    volatility_score = min(max(volatility_score, 0), 1)
    confidence_score = min(max(confidence_score, 0), 1)

    drift_component = (1 - drift_value) ** 2
    volatility_component = (1 - volatility_score)
    confidence_component = confidence_score

    health_index = (
        drift_component * 0.5 +
        volatility_component * 0.25 +
        confidence_component * 0.25
    )

    return round(min(max(health_index, 0), 1), 4)

def get_operational_mode(health_index: float) -> str:
    if health_index >= 0.85:
        return "aggressive"

    elif health_index >= 0.7:
        return "normal"

    elif health_index >= 0.6:
        return "cautious"

    else:
        return "safe_lock" 