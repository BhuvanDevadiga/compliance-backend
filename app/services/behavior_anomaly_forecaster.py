from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.behavior_memory import BehaviorMemory

FORECAST_WINDOW = 8 

def forecast_behavior_anomaly(db: Session, tenant_id: str):

    records = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(desc(BehaviorMemory.timestamp))
        .limit(FORECAST_WINDOW)
        .all()
    )

    if len(records) < 4:
        return {
            "forecast_alert": False,
            "reason": "insufficient history",
            "velocity": 0,
            "volatility_shift": False,
            "window_size": len(records),
        }
    scores = [r.behavior_score for r in reversed(records)]

    oscillation = sum(
        abs(scores[i] - scores[i - 1])
        for i in range(1, len(scores))
    )

    sustained_high = sum(1 for s in scores if s > 0.7)

    volatility_cluster = sum(
        1 for r in records if r.volatility == "spike"
    )

    instability_index = (
        oscillation * 0.4
        + sustained_high * 0.3
        + volatility_cluster * 0.3
    )

    forecast_alert = instability_index > 1.2

    return {
        "forecast_alert": forecast_alert,
        "confidence": round(instability_index, 2),
        "metrics": {
            "oscillation": round(oscillation, 2),
            "sustained_high": sustained_high,
            "volatility_cluster": volatility_cluster,
        },
    }
