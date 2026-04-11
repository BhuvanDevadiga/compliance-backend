from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.models.risk_history import RiskHistory
import numpy as np

def predict_risk_horizon(db: Session, tenant_id: str, horizon: int = 5):
    try:
        records = (
            db.query(RiskHistory)
            .filter(RiskHistory.tenant_id == tenant_id)
            .order_by(RiskHistory.created_at.desc())
            .limit(8)
            .all()
        )
    except OperationalError:
        return {
            "forecast_available": False,
            "message": "risk_history table is missing; run startup/migrations first",
        }

    if horizon < 1:
        return {
            "forecast_available": False,
            "message": "horizon must be >= 1",
        }

    if len(records) == 1:
        current = float(records[0].probability or 0.0)
        # Fallback: infer trend from latest velocity when only one data point exists.
        raw_velocity = float(records[0].velocity or 0.0)
        slope = raw_velocity if abs(raw_velocity) >= 0.001 else 0.02
        forecast = np.array([current + slope * (i + 1) for i in range(horizon)])
        forecast = np.clip(forecast, 0.0, 1.0)

        trend_slope = round(float(slope), 2)
        forecast_next = [round(float(v), 2) for v in forecast.tolist()]
        expected_peak = round(float(max(forecast_next)), 2)

        if slope > 0.001:
            direction = "increasing"
        elif slope < -0.001:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "forecast_available": True,
            "trend_slope": trend_slope,
            "forecast_next": forecast_next,
            "expected_peak": expected_peak,
            "direction": direction,
        }

    if len(records) < 2:
        return {
            "forecast_available": False,
            "message": "Not much available data",
        }
    

    probs = [r.probability for r in reversed(records)]
    x = np.arange(len(probs))
    y = np.array(probs)
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(probs), len(probs) + horizon)
    forecast = slope * future_x + intercept
    forecast = np.clip(forecast, 0.0, 1.0)

    trend_slope = round(float(slope), 2)
    forecast_next = [round(float(v), 2) for v in forecast.tolist()]
    expected_peak = round(float(max(forecast_next)), 2)

    volatility = float(np.std(y))
    volatility_score = round(volatility, 3)


    if slope > 0.001:
        direction = "increasing"
    elif slope < -0.001:
        direction = "decreasing"
    else:
        direction = "stable"

    if volatility_score > 0.2:
        risk_state = "chaotic"
    elif abs(trend_slope) > 0.05:
        risk_state = "trending"
    else:
        risk_state = "stable"      

    return {
        "forecast_available": True,
        "trend_slope": trend_slope,
        "forecast_next": forecast_next,
        "expected_peak": expected_peak,
        "direction": direction,
        "volatility_score": volatility_score,
        "risk_state": risk_state,
    }


def predect_risk_horizon(db: Session, tenant_id: str, horizon: int = 5):
    return predict_risk_horizon(db, tenant_id, horizon)

def get_forecast_accuracy(db, tenant_id):
    from app.models.forecast_evaluation import ForecastEvaluation

    records = (
        db.query(ForecastEvaluation)
        .filter(ForecastEvaluation.tenant_id == tenant_id)
        .order_by(ForecastEvaluation.created_at.desc())
        .limit(10)
        .all()
    )

    if not records:
        return None

    weighted_error = 0
    total_weight = 0

    for i, r in enumerate(records):
        weight = len(records) - i  # recent records higher weight
        weighted_error += r.error * weight
        total_weight += weight

    avg_error = weighted_error / total_weight
    accuracy = max(0.0, 1 - avg_error)

    return round(accuracy, 3)