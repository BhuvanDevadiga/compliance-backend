from sqlalchemy.orm import Session
from app.services.tenant_risk_engine import compute_tenant_risk
from app.services.intelligence_timeseries import build_timeseries
from app.services.health_service import get_exploration_multiplier

def compute_governance_adjustments(db: Session, tenant_id: str):

    risk_data = compute_tenant_risk(db, tenant_id)
    ts = build_timeseries(db, tenant_id)

    risk_score = risk_data["tenant_risk_score"]

    health_series = ts["health_index_trend"]

    if len(health_series) < 2:
        slope = 0
    else:
        slope = health_series[-1]["value"] - health_series[0]["value"]

    if risk_score > 0.6:
        mode = "high_risk"
        threshold_adjustment = -0.05
        strict_bias = 0.3
        base_exploration_rate = 0.2

    elif risk_score > 0.3:
        mode = "moderate_risk"
        threshold_adjustment = -0.02
        strict_bias = 0.2
        base_exploration_rate = 0.3

    else:
        mode = "stable"
        threshold_adjustment = +0.02
        strict_bias = 0.1
        base_exploration_rate = 0.4

    exploration_multiplier = get_exploration_multiplier(db, tenant_id)
    exploration_rate = base_exploration_rate * exploration_multiplier

    return {
        "tenant_id": tenant_id,
        "risk_score": risk_score,
        "system_mode": mode,
        "health_trend_slope": slope,
        "recommended_changes": {
            "adaptive_threshold_adjustment": threshold_adjustment,
            "strict_action_bias": strict_bias,
            "bandit_exploration_rate": exploration_rate
        }
    }
