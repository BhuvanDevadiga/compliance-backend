import math


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def compute_instability_probability(
    rolling_regret: float,
    regret_trend: float,
    exploration_rate: float,
    strict_actions: int,
    volatility: float
) -> float:

    
    score = (
        3.0 * rolling_regret +
        2.0 * regret_trend +
        1.5 * exploration_rate +
        0.5 * strict_actions +
        2.5 * volatility
    )

    return round(sigmoid(score), 4)

def get_instability_features(metrics: dict) -> dict:

    trend_map = {
        "increasing": 1.0,
        "stable": 0.5,
        "decreasing": 0.0
    }

    return {
        "rolling_regret": metrics.get("rolling_average_regret", 0),
        "regret_trend": trend_map.get(metrics.get("trend"), 0.5),
        "exploration_rate": metrics.get("effective_exploration_rate", 0.3),
        "strict_actions": metrics.get("strict_actions", 0),
        "volatility": abs(metrics.get("trend_slope", 0))
    }

