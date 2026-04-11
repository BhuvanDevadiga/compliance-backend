from datetime import datetime, timedelta


def apply_behavior_mitigation(
    db,
    tenant_id,
    behavior_profile,
    predictive_override: bool = False,
    escalation_override: bool = False,
    fatigue_override: bool = False,
    tenant_score_override=None,
    policy_state_override=None,
    trend_override: bool = False,
    forecast_override: bool = False,
    classification: str | None = None,
    policy_mode="NORMAL"
):
    score = float(behavior_profile.get("behavior_score", 0.0))
    volatility = behavior_profile.get("volatility")
    tenant_score_value = None

    if isinstance(tenant_score_override, dict):
        tenant_score_raw = tenant_score_override.get("score")
    else:
        tenant_score_raw = tenant_score_override

    if tenant_score_raw is not None:
        try:
            tenant_score_value = float(tenant_score_raw)
        except (TypeError, ValueError):
            tenant_score_value = None

    mitigation = "none"
    cooldown_until = None

    if forecast_override:
        mitigation = "lockdown"
        cooldown_until = datetime.utcnow() + timedelta(minutes=10)
    elif (
        predictive_override
        or escalation_override
        or trend_override
        or (tenant_score_value is not None and tenant_score_value >= 3.0)
        or score >= 0.7
        or volatility in {"chaotic", "spike"}
    ):
        mitigation = "throttle"
        cooldown_until = datetime.utcnow() + timedelta(minutes=5)
    elif (
        score >= 0.5
        or classification == "elevated behavior"
        or (tenant_score_value is not None and tenant_score_value >= 2.0)
    ):
        mitigation = "monitor"

        # --- policy-aware adjustment ---

    if policy_mode == "RELAXED":
      if mitigation == "throttle":
        mitigation = "monitor"

    elif policy_mode == "STRICT":
      if mitigation == "monitor":
        mitigation = "throttle"


    return {
        "tenant": tenant_id,
        "mitigation": mitigation,
        "cooldown_until": cooldown_until,
        "predictive_override": predictive_override,
        "escalation_override": escalation_override,
        "fatigue_override": fatigue_override,
        "tenant_score_override": tenant_score_override,
        "policy_state_override": policy_state_override,
        "trend_override": trend_override,
        "forecast_override": forecast_override,
        "classification": classification,
    }
