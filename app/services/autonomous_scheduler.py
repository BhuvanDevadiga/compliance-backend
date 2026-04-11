from apscheduler.schedulers.background import BackgroundScheduler
import os
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.autonomous_loop import run_autonomous_feedback_cycle
from app.models.tenant import Tenant
from app.services.auto_mitigation_router import auto_route_mitigation
from app.services.mitigation_learning_tuner import tune_mitigation_strategy
from app.services.tenant_behavior_profile_engine import update_tenant_profile
from app.services.escalation_probability_engine import compute_escalation_probability
from app.services.dynamic_scheduler_engine import resolve_dynamic_interval
from app.services.mitigation_optimizer_engine import update_strategy_performance
from app.models.risk_history import RiskHistory
from app.services.risk_forecasting import predict_risk_horizon
from app.services.risk_forecast import forecast_risk
from app.models.forecast_evaluation import ForecastEvaluation
from app.services.risk_forecasting import get_forecast_accuracy
from app.models.autonomous_decision_log import AutonomousDecisionLog
from app.services.reinforcement_engine import update_reinforcement
from app.ml.anomaly_detector import run_tenant_anomaly_detection
from app.models.mitigation_memory import MitigationMemory
from app.models.mitigation_strategy_performance import MitigationStrategyPerformance
from app.services.adaptive_threshold import update_adaptive_threshold
from app.services.strategy_bandit import apply_bandit_strategy
from app.services.mitigation_engine import log_mitigation_event
from app.services.ml_retrain_controller import controlled_retrain_if_needed
from app.models.ml_metadata import MLModelMetadata
from app.services.ml_health_service import get_ml_health_report
from app.models.decision_audit import DecisionAudit
from app.models.tenant_drift_log import TenantDriftLog
from app.services.health_index import compute_health_index, get_operational_mode
from app.models.tenant_health import TenantHealthSnapshot
from app.models.decision_trace import DecisionTrace
from app.services.governance_controller import compute_governance_adjustments
from app.services.bandit_service import select_strategy
from app.models.mitigation_strategy import MitigationStrategy
from app.services.mitigation_engine import choose_mitigation
from app.core.transaction import run_in_transaction



scheduler = BackgroundScheduler()

def autonomous_cycle_tenant(db: Session, tenant_id: str):
    base_threshold = 0.55
    escalation_score = 0.0
    proactive_escalation = False
    mitigation_override = None
    health_index = 0.8

    prob = compute_escalation_probability(db, tenant_id, source="scheduler_decision")
    raw_probability = prob["probability"]
    rule_probability = prob.get("rule_probability", 0.0)
    hybrid_probability = (0.4 * raw_probability) + (0.6 * rule_probability)
    print("[HYBRID - SCHEDULER]", hybrid_probability)

    db.add(
        RiskHistory(
            tenant_id=tenant_id,
            probability=raw_probability,
            velocity=prob.get("velocity", 0),
            stability=prob.get("stability", 0),
        )
    )
    # Commit is handled at a higher level.
    db.flush()

    # Persist escalation history from the RiskAssessment-based forecaster.
    escalation_forecast = forecast_risk(db, tenant_id, hybrid_probability, horizon=5)
    if not escalation_forecast.get("forecast_available"):
        print("[ESCALATION FORECAST SKIPPED]", escalation_forecast.get("reason"))

    forecast = predict_risk_horizon(db, tenant_id, horizon=5)
    predicted_peak = forecast.get("expected_peak")
    print("[FORECAST]", forecast)

    accuracy = get_forecast_accuracy(db, tenant_id)

    if forecast.get("forecast_available") and accuracy is not None:
        if accuracy < 0.7:
            print("[FORECAST IGNORED] Low reliability")
        else:
            if accuracy > 0.9:
                base_threshold = 0.55
            elif accuracy > 0.8:
                base_threshold = 0.55
            else:
                base_threshold = 0.65
            escalation_score = 0.0

            ml_health = get_ml_health_report(db)
            avg_confidence = ml_health.get("avg_confidence")
            confidence_for_health = avg_confidence if avg_confidence is not None else 0.5
            volatility_score = 1 - prob.get("stability", 0.5)

            health_index = compute_health_index(
                prob.get("drift", 0),
                volatility_score,
                confidence_for_health,
            )

            print("[HEALTH INDEX USED]", health_index)

            if health_index < 0.6:
                base_threshold += 0.12
            elif health_index < 0.7:
                base_threshold += 0.08
            elif health_index < 0.8:
                base_threshold += 0.05
            elif health_index < 0.9:
                base_threshold += 0.02

            base_threshold = min(max(base_threshold, 0.55), 0.7)
            print("[SAFE-FIRST THRESHOLD]", base_threshold)

            if forecast["expected_peak"] > base_threshold:
                escalation_score += 1
            if forecast.get("risk_state") == "chaotic":
                escalation_score += 0.5
            if forecast.get("direction") == "increasing":
                escalation_score += 0.5

            print("[ESCALATION SCORE]", escalation_score)
            if escalation_score >= 1:
                proactive_escalation = True
                print("[PROACTIVE ALERT] Adaptive composite trigger")

    base_threshold = max(0.3, min(base_threshold, 0.85))
    print("[FINAL THRESHOLD]", base_threshold)
    print("[PRE-MITIGATION PROBABILITY]", raw_probability)

    interval = resolve_dynamic_interval(raw_probability)
    _ = run_autonomous_feedback_cycle(db, tenant_id)

    memory_bias = (
        db.query(MitigationMemory)
        .filter(MitigationMemory.tenant_id == tenant_id)
        .order_by(MitigationMemory.reinforcement_score.desc())
        .first()
    )
    if memory_bias and memory_bias.reinforcement_score > 0:
        mitigation_override = memory_bias.mitigation_type

    hybrid_score = (0.6 * escalation_score) + (0.4 * raw_probability)
    print(
        f"[HYBRID] rule={escalation_score:.3f} "
        f"ml={raw_probability:.3f} "
        f"hybrid={hybrid_score:.3f}"
    )

    if proactive_escalation:
        if hybrid_score >= 1.5 and accuracy > 0.85:
            mitigation_override = "strict_action"
        elif hybrid_score >= 1 and accuracy > 0.75:
            mitigation_override = "warning"
        else:
            mitigation_override = None

    decision_flag = hybrid_score >= base_threshold
    print("[DECISION CHECK]", hybrid_score, ">=", base_threshold, "->", decision_flag)
    print("HYBRID:", hybrid_score, "THRESHOLD:", base_threshold)

    aggressive_threshold = base_threshold + 0.2
    active_threshold = base_threshold
    if hybrid_score >= aggressive_threshold:
        level = "aggressive"
    elif hybrid_score >= active_threshold:
        level = "active"
    else:
        level = "advisory"

    mitigation = choose_mitigation(
        db=db,
        tenant_id=tenant_id,
        risk_level=level,
        override=mitigation_override,
    )
    print("✅ UNIFIED ENGINE CALLED")
    print("RISK LEVEL:", level)

    ucb_strategy = select_strategy(db, tenant_id, level)
    if ucb_strategy:
        mitigation["recommended_mitigation"] = ucb_strategy
        print("[UCB STRATEGY]", ucb_strategy)

    bandit = apply_bandit_strategy(
        db,
        tenant_id,
        mitigation.get("recommended_mitigation"),
        mitigation.get("level"),
    )
    mitigation["recommended_mitigation"] = bandit["strategy"]
    print("[BANDIT MODE]", bandit["mode"])

    selected_mitigation = mitigation.get("recommended_mitigation")
    final_mitigation = mitigation_override or selected_mitigation

    print("[MITIGATION BEFORE HEALTH CEILING]", final_mitigation)
    print("[HEALTH FOR CEILING]", health_index)

    if health_index < 0.6:
        final_mitigation = "advisory_notice"
    elif health_index < 0.7:
        if final_mitigation in ["warning", "strict_action"]:
            final_mitigation = "advisory_notice"
    elif health_index < 0.8:
        if final_mitigation == "strict_action":
            final_mitigation = "warning"

    mitigation["recommended_mitigation"] = final_mitigation
    print("[MITIGATION AFTER HEALTH CEILING]", mitigation["recommended_mitigation"])

    if selected_mitigation and selected_mitigation != final_mitigation:
        record_strategy_play(
            db=db,
            tenant_id=tenant_id,
            strategy_name=selected_mitigation,
            level=mitigation.get("level"),
        )
        print(
            "[STRATEGY OVERRIDDEN]",
            selected_mitigation,
            "->",
            final_mitigation,
        )

    mode = get_operational_mode(health_index)
    print("[OPERATIONAL MODE]", mode)
    print("Auto mitigation:", mitigation)

    if mitigation.get("recommended_mitigation"):
        log_mitigation_event(
            db=db,
            tenant_id=tenant_id,
            action=mitigation["recommended_mitigation"],
            prediction=mitigation.get("level", "scheduler"),
            context={
                "stage": "autonomous_scheduler",
                "forecast_peak": predicted_peak,
                "forecast_accuracy": accuracy,
                "proactive_escalation": proactive_escalation,
                "selected_mitigation": selected_mitigation,
                "executed_mitigation": final_mitigation,
            },
            ml_probability=raw_probability,
            hybrid_score=hybrid_score,
            rule_score=escalation_score,
        )

    recommended = mitigation.get("recommended_mitigation")
    base_confidence = mitigation.get("confidence", 1.0)
    memory = (
        db.query(MitigationMemory)
        .filter(
            MitigationMemory.tenant_id == tenant_id,
            MitigationMemory.mitigation_type == recommended,
        )
        .first()
    )
    reinforcement_score = memory.reinforcement_score if memory else 0.0
    adaptive_confidence = round(base_confidence * (1 + reinforcement_score), 4)
    print(
        "[ADAPTIVE CONFIDENCE]",
        recommended,
        "| base:", base_confidence,
        "| reinforcement:", reinforcement_score,
        "| final:", adaptive_confidence,
    )
    mitigation["adaptive_confidence"] = adaptive_confidence

    learning = tune_mitigation_strategy(db, tenant_id)
    print("[LEARNING]", learning)
    profile = update_tenant_profile(db, tenant_id)
    print("[PROFILE]", profile)
    threshold_info = update_adaptive_threshold(db, tenant_id)
    print("[ADAPTIVE THRESHOLD]", threshold_info)
    print("[ESCALATION PROBABILITY]", prob)
    perf = update_strategy_performance(
        db,
        tenant_id,
        mitigation.get("recommended_mitigation"),
    )
    print("[STRATEGY PERFORMANCE]", perf)

    if predicted_peak is not None:
        actual_probability = raw_probability
        error = abs(predicted_peak - raw_probability)
        db.add(
            ForecastEvaluation(
                tenant_id=tenant_id,
                predicted_peak=predicted_peak,
                actual_next=actual_probability,
                error=error,
            )
        )
        # Commit is handled at a higher level.
        db.flush()
        print("[FORECAST ERROR]", round(error, 3))

        accuracy = get_forecast_accuracy(db, tenant_id)
        print("[FORECAST ACCURACY]", accuracy)

    trace = DecisionTrace(
        tenant_id=tenant_id,
        probability=raw_probability,
        hybrid_score=hybrid_score,
        health_index=health_index,
        accuracy=accuracy,
        pre_mitigation=selected_mitigation,
        final_mitigation=mitigation["recommended_mitigation"],
        threshold_used=base_threshold,
        drift_value=prob.get("drift", 0.0),
        forecast_state=forecast.get("risk_state"),
        bandit_confidence=mitigation.get("confidence"),
    )

    db.add(trace)
    # Commit is handled at a higher level.
    db.flush()

    print(
        f"[AUTO LOOP] {tenant_id} | "
        f"PROB={prob['probability']} | "
        f"STRATEGY={mitigation.get('recommended_mitigation')} | "
        f"next cycle ~{interval}s"
    )

    print("[ACCURACY]", accuracy)
    print("[ADAPTIVE THRESHOLD USED]", base_threshold)
    print("[ESCALATION SCORE]", escalation_score)

    decision_log = AutonomousDecisionLog(
        tenant_id=tenant_id,
        forecast_peak=forecast.get("expected_peak"),
        forecast_accuracy=accuracy,
        escalation_score=escalation_score,
        proactive_triggered=proactive_escalation,
        mitigation_level=mitigation_override or mitigation.get("recommended_mitigation"),
        final_probability=raw_probability,
    )
    db.add(decision_log)
    # Commit is handled at a higher level.
    db.flush()
    db.refresh(decision_log)

    previous_decision = (
        db.query(AutonomousDecisionLog)
        .filter(AutonomousDecisionLog.tenant_id == tenant_id)
        .order_by(AutonomousDecisionLog.created_at.desc())
        .offset(1)
        .first()
    )

    if previous_decision:
        print("Previous mitigation:", previous_decision.mitigation_level)
        update_reinforcement(
            db=db,
            tenant_id=tenant_id,
            mitigation_type=previous_decision.mitigation_level,
            previous_probability=previous_decision.final_probability,
            current_probability=raw_probability,
        )

    print("[DECISION LOGGED]")
    print(">>> Reinforcement section reached")

    tenant_row = (
        db.query(Tenant)
        .filter(Tenant.tenant_id == tenant_id)
        .first()
    )
    retrain_status = {"status": "no_retrain_needed"}
    if tenant_row:
        retrain_status = controlled_retrain_if_needed(db, tenant_row.tenant_id)
        print("[RETRAIN CHECK]", retrain_status)
    else:
        print(f"[RETRAIN CHECK] skipped, tenant not found: {tenant_id}")

    latest_drift = (
        db.query(TenantDriftLog)
        .filter(TenantDriftLog.tenant_id == tenant_id)
        .order_by(TenantDriftLog.created_at.desc())
        .first()
    )
    drift_value = latest_drift.drift_value if latest_drift else 0.0

    audit = DecisionAudit(
        tenant_id=tenant_id,
        ml_probability=raw_probability,
        rule_score=escalation_score,
        hybrid_score=hybrid_score,
        threshold_used=base_threshold,
        forecast_trend=None,
        forecast_peak=predicted_peak,
        drift_value=latest_drift.drift_value if latest_drift else None,
        drift_streak=latest_drift.drift_streak if latest_drift else 0,
        retrain_triggered=(retrain_status.get("status") == "retrained"),
        strategy_selected=(mitigation_override or mitigation.get("recommended_mitigation") or "none"),
        confidence_score=min(max(adaptive_confidence, 0), 1),
    )
    db.add(audit)
    # Commit is handled at a higher level.
    db.flush()

    volatility_score = 1 - prob.get("stability", 0.5)
    health_index = compute_health_index(
        drift_value,
        volatility_score,
        min(max(adaptive_confidence, 0), 1),
    )

    snapshot = TenantHealthSnapshot(
        tenant_id=tenant_id,
        health_index=health_index,
        drift_value=drift_value,
        confidence_score=adaptive_confidence,
        volatility_score=volatility_score,
    )

    db.add(snapshot)
    # Commit is handled at a higher level.
    db.flush()
    print(f"[HEALTH INDEX] {tenant_id} -> {round(health_index, 4)}")

    health = get_ml_health_report(db)
    print("[ML HEALTH]", health)

    try:
        autotune = apply_governance_autotune(db, tenant_id)
        print("[AUTONOMOUS GOVERNANCE]", autotune)
    except Exception as gov_error:
        print(f"[Governance Error] {tenant_id} -> {gov_error}")


def autonomous_cycle_job(db: Session):
    tenants = get_active_tenants(db)
    for tenant_id in tenants:
        try:
            run_in_transaction(SessionLocal, autonomous_cycle_tenant, tenant_id=tenant_id)
        except Exception as e:
            print(f"[Auto Loop Error] {tenant_id} -> {e}")
    refresh_audit_anomalies(db)


def autonomous_cycle_job_runner():
    run_in_transaction(SessionLocal, autonomous_cycle_job)

def start_autonomous_scheduler():
    interval_seconds = int(os.getenv("AUTONOMOUS_CYCLE_INTERVAL_SECONDS", "180"))
    scheduler.add_job(autonomous_cycle_job_runner, 
                        trigger='interval', 
                        seconds=interval_seconds,  
                        id='autonomous_cycle_job',
                        replace_existing=True)        
    scheduler.start()

def get_all_tenants(db):
   return db.query(Tenant).all()

def refresh_audit_anomalies(db):
    tenants = get_all_tenants(db)
    for tenant in tenants:
        run_tenant_anomaly_detection(tenant.tenant_id)

def get_active_tenants(db):
   tenant = db.query(Tenant).all()
   return [t.tenant_id for t in tenant]   


def record_strategy_play(db, tenant_id, strategy_name, level=None):
    if not strategy_name:
        return

    query = (
        db.query(MitigationStrategy)
        .filter(
            MitigationStrategy.tenant_id == tenant_id,
            MitigationStrategy.strategy == strategy_name,
        )
    )
    if level:
        query = query.filter(MitigationStrategy.level == level)
    strategy = query.first()

    if not strategy:
        strategy = MitigationStrategy(
            tenant_id=tenant_id,
            level=level,
            strategy=strategy_name,
            total_plays=0,
            total_reward=0.0,
            average_reward=0.0,
        )
        db.add(strategy)

    strategy.total_plays += 1
    strategy.average_reward = (
        strategy.total_reward / strategy.total_plays
    )
    # Commit is handled at a higher level.
    db.flush()

def apply_governance_autotune(db, tenant_id):

    governance = compute_governance_adjustments(db, tenant_id)

    changes = governance["recommended_changes"]

    threshold_adjustment = changes["adaptive_threshold_adjustment"]
    strict_bias = changes["strict_action_bias"]
    exploration_rate = changes["bandit_exploration_rate"]

    print("[GOVERNANCE AUTOTUNE]", {
        "tenant": tenant_id,
        "threshold_adj": threshold_adjustment,
        "strict_bias": strict_bias,
        "exploration": exploration_rate
    })

    return {
        "threshold_adjustment": threshold_adjustment,
        "strict_bias": strict_bias,
        "exploration_rate": exploration_rate
    }
