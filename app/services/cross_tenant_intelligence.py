from sqlalchemy.orm import Session
from app.models.behavior_memory import BehaviorMemory


def analyze_cross_tenant_patterns(
    db: Session,
    window: int = 50,
):
    """
    Aggregates recent behavior across all tenants
    to detect system-wide instability patterns.
    """

    history = (
        db.query(BehaviorMemory)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(window)
        .all()
    )

    if len(history) < 10:
        return {
            "global_alert": False,
            "reason": "insufficient global history",
        }

    critical_ratio = sum(
        1 for h in history if h.classification == "critical behavior"
    ) / len(history)

    volatility_spikes = sum(
        1 for h in history if h.volatility == "spike"
    )

    global_alert = critical_ratio > 0.5 or volatility_spikes > window * 0.4

    return {
        "global_alert": global_alert,
        "critical_ratio": round(critical_ratio, 2),
        "volatility_spikes": volatility_spikes,
        "window": window,
    }
