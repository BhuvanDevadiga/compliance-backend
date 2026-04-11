from app.models.risk_assessment import RiskAssessment
from sqlalchemy.orm import Session
from app.services.escalation_engine import (
    classify_escalation,
    detect_escalation_streak,
    compute_severity_score,
)
from app.models.escalation_log import EscalationLog


MODEL_VERSION = "1.0"

def linear_regression_slope(values):
    if len(values) < 2:
        return 0.0

    x = list(range(len(values)))
    n = len(values)

    mean_x = sum(x) / n
    mean_y = sum(values) / n

    numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0

    return numerator / denominator

def forecast_risk(
    db: Session,
    tenant_id: str,
    hybrid_probability: float | None = None,
    horizon: int = 5,
):
    records = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.tenant_id == tenant_id)
        .order_by(RiskAssessment.created_at.asc())
        .all()
    )

    if len(records) < 5:
        return {
            "forecast_available": False,
            "reason": "insufficient_data"
        }

    # Keep only numeric scores to avoid None arithmetic during forecasting.
    values = [r.risk_score for r in records[-20:] if r.risk_score is not None]  # last 20 samples

    if len(values) < 2:
        return {
            "forecast_available": False,
            "reason": "insufficient_numeric_data"
        }

    slope = linear_regression_slope(values)

    last_value = values[-1]

    forecast = []
    for i in range(1, horizon + 1):
        forecast.append(last_value + slope * i)

    expected_peak = max(forecast)
    forecast_avg = sum(forecast) / len(forecast)

    normalized_probability = hybrid_probability
    if normalized_probability is None:
        normalized_probability = forecast_avg / 100 if forecast_avg > 1 else forecast_avg
    normalized_probability = max(0.0, min(float(normalized_probability), 1.0))
    print("DEBUG FORECAST_RISK HYBRID:", hybrid_probability)

    escalation = classify_escalation(normalized_probability, slope)
    updated_signal = detect_escalation_streak(
        db,
        tenant_id=tenant_id,
        current_signal=escalation["escalation_signal"]
    )
    escalation["escalation_signal"]= updated_signal

    severity_score = compute_severity_score(
        normalized_probability,
        slope,
        escalation["escalation_signal"],
    )
        
    

    log = EscalationLog(
        tenant_id=tenant_id,
        escalation_signal=escalation["escalation_signal"],
        recommended_action=escalation["recommended_action"],
        trend_slope=slope,
        forecast_avg=forecast_avg,
        expected_peak=expected_peak,
        model_version=MODEL_VERSION,
        severity_score=severity_score,
    )

    db.add(log)
    # Commit is handled at a higher level.
    db.flush()

    return {
        "forecast_available": True,
        "trend_slope": slope,
        "forecast_next": forecast,
        "expected_peak": expected_peak,
        **escalation
    }
