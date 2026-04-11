from sqlalchemy.orm import Session

from app.services.behavior_mitigation import apply_behavior_mitigation
from app.services.predictive_escalation import predict_escalation
from app.services.adaptive_policy_engine import BehaviorSnapshot
from app.services.preemptive_override import trigger_preemptive_override
from app.models.behavior_memory import BehaviorMemory
from app.services.behavior_trend_analyzer import analyze_behavior_trend
from app.services.behavior_anomaly_forecaster import forecast_behavior_anomaly
from app.services.behavior_escalation_engine import evaluate_behavior_escalation
from app.services.escalation_fatigue_engine import detect_escalation_fatigue
from app.services.tenant_behavior_scoring import compute_tenant_behavior_score
from app.services.policy_evolution_engine import evolve_tenant_policy
from app.services.mitigation_feedback_engine import record_mitigation_outcome






def analyze_behavior(
    db: Session,
    tenant_id: str,
    behavior_score: float,
    volatility: str,
):
    """
    Behavior intelligence pipeline:

    classification → prediction → mitigation
    """

    # ======================================================
    # 1️⃣ Classification logic (unchanged)
    # ======================================================

    if behavior_score < 0.3:
        classification = "stable behavior"
    elif behavior_score < 0.7:
        classification = "elevated behavior"
    else:
        classification = "critical behavior"

    behavior_profile = {
        "behavior_score": behavior_score,
        "volatility": volatility,
        "classification": classification,
    }

    # --- trend intelligence ---
    trend = analyze_behavior_trend(db, tenant_id)
    behavior_profile["trend"] = trend

    trend_override = trend["trend_alert"]
    forecast = forecast_behavior_anomaly(db, tenant_id)
    forecast_override = forecast.get("forecast_alert", False)
    
    escalation = evaluate_behavior_escalation(db, tenant_id)
    behavior_profile["escalation"] = escalation
    escalation_override = escalation["escalation"]

    fatigue = detect_escalation_fatigue(db, tenant_id)
    behavior_profile["fatigue"] = fatigue
    fatigue_override = fatigue["fatigue_detected"]

    tenant_score = compute_tenant_behavior_score(db, tenant_id)
    behavior_profile["tenant_score"] = tenant_score

    policy_state = evolve_tenant_policy(db, tenant_id)
    behavior_profile["adaptive_policy"] = policy_state




# --------------------------


    # ======================================================
    # 2️⃣ Build lightweight snapshot history
    # (replace with DB fetch later if desired)
    # ======================================================

    snapshots = [
        BehaviorSnapshot(tenant_id, behavior_score * 0.6, 0.2),
        BehaviorSnapshot(tenant_id, behavior_score * 0.8, 0.3),
        BehaviorSnapshot(tenant_id, behavior_score, 0.5),
    ]

    # ======================================================
    # 3️⃣ Predict escalation trend
    # ======================================================

    prediction = predict_escalation(tenant_id, snapshots)

    override_policy = trigger_preemptive_override(
    tenant_id,
    prediction,
)

    behavior_profile["preemptive_override"] = (
    override_policy.name if override_policy else None
)


    behavior_profile["prediction"] = {
        "score": prediction.score,
        "reason": prediction.reason,
        "should_escalate": prediction.should_escalate,
    }

    # ======================================================
    # 4️⃣ Mitigation decision (enhanced)
    # ======================================================

    mitigation = apply_behavior_mitigation(
        db=db,
        tenant_id=tenant_id,
        behavior_profile=behavior_profile,
        trend_override=trend_override,
        forecast_override=forecast_override,
        predictive_override = prediction.should_escalate,
        escalation_override=escalation_override,
        classification=classification,
        fatigue_override=fatigue_override,
        tenant_score_override=tenant_score,
        policy_state_override=policy_state,
        policy_mode=policy_state["policy_mode"],

    
    )
    


    behavior_profile["mitigation"] = mitigation
    behavior_profile["trend"] = trend
    behavior_profile["forecast"] = forecast
    

    # --- behavior memory persistence ---
    memory_entry = BehaviorMemory(
        tenant_id=tenant_id,
        behavior_score=behavior_score,
        volatility=volatility,
        classification=classification,
)
    # naive outcome heuristic (placeholder learning signal)
    behavior_improved = behavior_score < 0.6

    record_mitigation_outcome(
    db=db,
    tenant_id=tenant_id,
    mitigation_action=mitigation["mitigation"],
    behavior_improved=behavior_improved,
)

    
    


    db.add(memory_entry)
    db.commit()
# -----------------------------------


    return behavior_profile
