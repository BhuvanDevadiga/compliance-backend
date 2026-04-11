
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.mitigation_strategy import MitigationStrategy
import random, json
from app.services.risk_forecasting import predict_risk_horizon
from app.services.bandit_utils import beta_bounds
from app.models.decision_snapshot import DecisionSnapshot
from app.services.ledger_utils import compute_hash
from app.core.engine_config import (
    BASELINE_STRATEGY,
    MAX_ALLOWED_REGRET,
    AUTO_FREEZE_ON_REGRET,
)
from app.core.governance_guard import require_engine_version
from app.services.decision_ledger_service import write_decision_snapshot
from app.core.engine_config import ENGINE_VERSION
from packaging import version
from app.services.governance_service import attempt_auto_unfreeze
from app.services.governance_service import log_governance_event, log_ml_decision
from app.services.health_service import get_exploration_multiplier
from app.services.tenant_state_service import get_tenant_state
from app.services.platform_governance_service import get_global_state, attempt_platform_unfreeze
from app.services.instability_model import compute_instability_probability, get_instability_features
from app.services.risk_metrics_service import get_regret_risk_index
from app.core.tenant_lock import acquire_tenant_lock

STRATEGY_PRIORS = {
    "advisory_notice": (2,3),
    "monitor": (3,2),
    "warning": (2,3),
    "rate_limit": (2,3),
    "full_restriction": (1,4),
    "lockdown":(1,5),
} 


@require_engine_version
def apply_dominance_retirement(db, strategies, strategy_stats):
    retired_any = False
    for s in strategy_stats:
        for other in strategy_stats:

            if s["strategy"] == other["strategy"]:
                continue

            # If fully dominated
            if s["ucb"] < other["lcb"]:
                record = next(
                    strat for strat in strategies
                    if strat.strategy == s["strategy"]
                )

                record.is_active = False
                record.retired_at = datetime.utcnow()
                retired_any = True

                print(f"⚠ Dominance retiring {s['strategy']}")
    if retired_any:
        # Commit is handled at a higher level.
        db.flush()

@require_engine_version
def select_strategy(db: Session, tenant_id: str, level: str):
    tenant_state = acquire_tenant_lock(db, tenant_id)
    state = get_tenant_state(db, tenant_id)
    global_state = get_global_state(db)
    if global_state and global_state.platform_override_active:
        unlocked = attempt_platform_unfreeze(db)
        if not unlocked:
            print("🚨 Platform override active. Returning baseline.")
            return BASELINE_STRATEGY

    # Enforce freeze lock even if adaptive_engine_frozen was manually toggled off.
    if state.freeze_locked_version and not state.adaptive_engine_frozen:
        if version.parse(ENGINE_VERSION) <= version.parse(state.freeze_locked_version):
            state.adaptive_engine_frozen = True
            if not state.freeze_reason:
                state.freeze_reason = "Manual unfreeze blocked; version bump required."
            if not state.frozen_at:
                state.frozen_at = datetime.utcnow()
            # Commit is handled at a higher level.
            db.flush()
            print("WARNING: Freeze lock enforced. Version bump required.")

    # If frozen -> attempt unlock
    if state.adaptive_engine_frozen:
        unlocked = attempt_auto_unfreeze(db, tenant_id)
        if not unlocked:
            print("? Adaptive engine frozen. Version bump required.")
            return BASELINE_STRATEGY

    # Step A: Get system metrics
    metrics = get_regret_risk_index(db)

    # Step B: Convert to ML features
    features = get_instability_features(metrics)

    # Step C: Compute instability probability
    instability_probability = compute_instability_probability(**features)

    # Step D: Decide exploration multiplier
    exploration_multiplier = 1.0

    if instability_probability > 0.7:
        exploration_multiplier = 0.5  # reduce exploration

    elif instability_probability < 0.3:
        exploration_multiplier = 1.2  # increase exploration

    print("RISK LEVEL:", level)

    strategies = db.query(MitigationStrategy).filter(
        MitigationStrategy.tenant_id == tenant_id,
        MitigationStrategy.level == level,
        MitigationStrategy.is_active == True
    ).all()

    if not strategies:
        print("No strategies found for level")
        return None

    forecast = predict_risk_horizon(db, tenant_id, horizon=5)
    volatility = forecast.get("volatility_score")
    context = "volatile" if volatility and volatility > 0.6 else "stable"
    print("CONTEXT:", context)

    best_sample = -1
    best_strategy = None

    strategy_stats = []
    samples = []

    for s in strategies:
        prior_success, prior_failure = STRATEGY_PRIORS.get(
            s.strategy, (1,1)
        )
        if context == "volatile":
            success = s.success_volatility or 0
            failure = s.failure_volatility or 0
        else:
            success = s.success_table or 0
            failure = s.failure_table or 0

        alpha = success + prior_success
        beta_param = failure + prior_failure

        lcb, ucb = beta_bounds(alpha, beta_param)
        strategy_stats.append({
            "model_id": s.id,
            "strategy": s.strategy,
            "alpha": alpha,
            "beta": beta_param,
            "lcb": lcb,
            "ucb": ucb,
            "posterior_mean": alpha / (alpha + beta_param),
        })

        sample = random.betavariate(alpha, beta_param)
        samples.append((sample, s.strategy))

        print(
            f"[TS] {s.strategy} | "
            f"alpha={alpha} beta={beta_param} "
            f"| sample={round(sample,4)}"
        )

        if sample > best_sample:
            best_sample = sample
            best_strategy = s.strategy

    BASE_EXPLORATION_RATE = 0.4
    effective_exploration_rate = BASE_EXPLORATION_RATE * exploration_multiplier
    effective_exploration_rate = max(0.0, min(1.0, effective_exploration_rate))

    print("Instability:", instability_probability)
    print("Exploration Multiplier:", exploration_multiplier)
    print("Effective Exploration:", effective_exploration_rate)

    if db.in_transaction():
        tenant_state = acquire_tenant_lock(db, tenant_id)
        log_ml_decision(
            db=db,
            tenant_id=tenant_id,
            instability_probability=instability_probability,
            exploration_multiplier=exploration_multiplier,
            effective_exploration_rate=effective_exploration_rate,
            risk_score=tenant_state.risk_score or 0.0,
        )
    else:
        with db.begin():
            tenant_state = acquire_tenant_lock(db, tenant_id)
            log_ml_decision(
                db=db,
                tenant_id=tenant_id,
                instability_probability=instability_probability,
                exploration_multiplier=exploration_multiplier,
                effective_exploration_rate=effective_exploration_rate,
                risk_score=tenant_state.risk_score or 0.0,
            )

    if random.random() < effective_exploration_rate:
        best_strategy = random.choice(strategies).strategy
        print(f"[EXPLORE] picked {best_strategy}")
    else:
        print(f"[EXPLOIT] picked {best_strategy}")

    apply_dominance_retirement(db, strategies, strategy_stats)

    print("[TS STRATEGY]", best_strategy)

    posterior_means = [s["posterior_mean"] for s in strategy_stats]
    optimal_expected = max(posterior_means)
    chosen_expected = next(
        s["posterior_mean"] for s in strategy_stats
        if s["strategy"] == best_strategy
    )
    regret = optimal_expected - chosen_expected

    print(
        f"[REGRET] optimal={optimal_expected:.6f} "
        f"chosen={chosen_expected:.6f} "
        f"regret={regret:.6f} threshold={MAX_ALLOWED_REGRET}"
    )

    if AUTO_FREEZE_ON_REGRET and regret >= MAX_ALLOWED_REGRET:
        state = get_tenant_state(db, tenant_id)
        state.adaptive_engine_frozen = True
        state.freeze_reason = f"Regret spike: {regret}"
        state.freeze_locked_version = ENGINE_VERSION
        state.frozen_at = datetime.utcnow()
        # Commit is handled at a higher level.
        db.flush()

        print(f"🚨 TENANT {tenant_id} FREEZE ACTIVATED")

        if not state.adaptive_engine_frozen:
            state.adaptive_engine_frozen = True
            state.freeze_reason = f"Regret spike: {regret}"
            state.frozen_at = datetime.utcnow()
            state.freeze_locked_version = ENGINE_VERSION

            # Commit is handled at a higher level.
            db.flush()
            if db.in_transaction():
                tenant_state = acquire_tenant_lock(db, tenant_id)
                log_governance_event(
                    db=db,
                    event_type="FREEZE",
                    tenant_id=tenant_id,
                    previous_version=ENGINE_VERSION,
                    reason=f"Regret spike: {regret}",
                )
            else:
                with db.begin():
                    tenant_state = acquire_tenant_lock(db, tenant_id)
                    log_governance_event(
                        db=db,
                        event_type="FREEZE",
                        tenant_id=tenant_id,
                        previous_version=ENGINE_VERSION,
                        reason=f"Regret spike: {regret}",
                    )

        print("?? GLOBAL FREEZE ACTIVATED:", state.freeze_reason)
        print("?? Freeze locked to engine version:", ENGINE_VERSION)

    random_seed = str(random.random())

    write_decision_snapshot(
        db=db,
        tenant_id=tenant_id,
        risk_level=level,
        context=context,
        strategy_stats=strategy_stats,
        selected_strategy=best_strategy,
        regret=regret,
        random_seed=random_seed,
    )

    return best_strategy

def choose_mitigation(db: Session, tenant_id: str, level: str):
    
    return select_strategy(db, tenant_id, level)

