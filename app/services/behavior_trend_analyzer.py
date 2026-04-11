from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.behavior_memory import BehaviorMemory


TREND_WINDOW = 5  # recent snapshots to analyze


def analyze_behavior_trend(db: Session, tenant_id: str):
    """
    Temporal intelligence layer.

    Looks at recent behavior memory and detects:
    - upward risk drift
    - volatility escalation
    """

    records = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(desc(BehaviorMemory.timestamp))
        .limit(TREND_WINDOW)
        .all()
    )

    if len(records) < 2:
        return {
            "trend_alert": False,
            "reason": "insufficient history",
            "velocity": 0,
            "volatility_shift": False,
        }

    scores = [r.behavior_score for r in reversed(records)]

    velocity = scores[-1] - scores[0]

    volatility_shift = any(
        r.volatility == "spike" for r in records
    )

    trend_alert = velocity > 0.25 or volatility_shift

    return {
        "trend_alert": trend_alert,
        "velocity": round(velocity, 3),
        "volatility_shift": volatility_shift,
        "window_size": len(records),
    }
