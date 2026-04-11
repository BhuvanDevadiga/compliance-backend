from sqlalchemy.orm import Session

from app.services.predictive_risk import predict_risk
from app.services.intelligent_alerts import intelligent_alert
from app.services.mitigation_engine import log_mitigation_event


def auto_mitigate(
    db: Session,
    tenant_id: str,
    override_strategy: str | None = None,
    ml_probability: float | None = None,
    hybrid_score: float | None = None,
    rule_score: float | None = None,
):
    forecast = predict_risk(db, tenant_id)
    prediction = forecast["prediction"]
    recommended_mitigation = None

    if prediction == "stable":
        recommended_mitigation = "none"
        if override_strategy:
            recommended_mitigation = override_strategy
        return {
            "action": recommended_mitigation,
            "recommended_mitigation": recommended_mitigation,
            "reason": "tenant stable",
        }

    if prediction == "risk_building":
        recommended_mitigation = "monitoring_escalated"
        if override_strategy:
            recommended_mitigation = override_strategy

        intelligent_alert(
            db=db,
            alert_key=f"mitigation_warning_{tenant_id}",
            tenant_id=tenant_id,
            event_type="mitigation_warning",
            payload={"stage": "early_warning"},
        )

        log_mitigation_event(
            db=db,
            tenant_id=tenant_id,
            action=recommended_mitigation,
            prediction=prediction,
            context={"stage": "early_warning", "forecast": forecast},
            ml_probability=ml_probability,
            hybrid_score=hybrid_score,
            rule_score=rule_score,
        )

        return {
            "action": recommended_mitigation,
            "recommended_mitigation": recommended_mitigation,
            "prediction": prediction,
        }

    if prediction == "imminent_critical_risk":
        recommended_mitigation = "auto_protection_triggered"
        if override_strategy:
            recommended_mitigation = override_strategy

        intelligent_alert(
            db=db,
            alert_key=f"mitigation_isolate_{tenant_id}",
            tenant_id=tenant_id,
            event_type="mitigation_auto_protection",
            payload={"stage": "auto_protection"},
        )

        log_mitigation_event(
            db=db,
            tenant_id=tenant_id,
            action=recommended_mitigation,
            prediction=prediction,
            context={"stage": "auto_protection", "forecast": forecast},
            ml_probability=ml_probability,
            hybrid_score=hybrid_score,
            rule_score=rule_score,
        )

        return {
            "action": recommended_mitigation,
            "recommended_mitigation": recommended_mitigation,
            "prediction": prediction,
        }

    recommended_mitigation = "none"
    if override_strategy:
        recommended_mitigation = override_strategy
    return {
        "action": recommended_mitigation,
        "recommended_mitigation": recommended_mitigation,
        "reason": f"unsupported prediction: {prediction}",
        "prediction": prediction,
    }
