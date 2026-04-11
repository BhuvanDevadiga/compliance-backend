from datetime import datetime
import random
from sqlalchemy.orm import Session
from app.models.mitigation_strategy import MitigationStrategy
from app.models.mitigation_log import MitigationLog
from app.services.risk_forecasting import predict_risk_horizon
from app.services.volatility import compute_volatility
from app.services.bandit_utils import beta_lower_bound
from app.core.governance_guard import require_engine_version


def log_mitigation_event(
    db: Session,
    tenant_id: str,
    action: str,
    prediction: str,
    context: dict | None = None,
    ml_probability: float | None = None,
    hybrid_score: float | None = None,
    rule_score: float | None = None,
):
    confidence = None
    if ml_probability is not None:
        confidence = abs(ml_probability - 0.5) * 2


    record = MitigationLog(
        tenant_id=tenant_id,
        action=action,
        prediction=prediction,
        context=context,
        timestamp=datetime.utcnow(),
        ml_probability=ml_probability,
        hybrid_score=hybrid_score,
        rule_score=rule_score,
        actual_escalated=0,
        confidence=confidence,
    )

    db.add(record)
    # Commit is handled at a higher level.

    strategy_query = db.query(MitigationStrategy).filter(
        MitigationStrategy.tenant_id == tenant_id,
        MitigationStrategy.strategy == action,
    )
    if prediction in STRATEGY_MAP:
        strategy_query = strategy_query.filter(
            MitigationStrategy.level == prediction
        )
    else:
        # Allow passing a concrete strategy name; map it back to a level.
        for level, strategies in STRATEGY_MAP.items():
            if prediction in strategies:
                strategy_query = strategy_query.filter(
                    MitigationStrategy.level == level
                )
                break

    strategy = strategy_query.first()
    if strategy:
        strategy.total_plays += 1
        # Commit is handled at a higher level.
        db.flush()
    # Keep side effects minimal in service layer; logging is handled upstream.



EXPLORATION_RATE = 0.05
DECAY = 0.9

STRATEGY_MAP = {
    "advisory": ["advisory_notice", "monitor"],
    "active": ["warning", "rate_limit"],
    "aggressive": ["temporary_block", "full_restriction"],
}


def choose_mitigation(
    db: Session,
    tenant_id: str,
    risk_level: str,
    override: str | None = None,
):
    # 1. Governance override
    if override:
        return {
            "recommended_mitigation": override,
            "confidence": 1.0,
            "level": risk_level,
        }

    candidates = STRATEGY_MAP.get(risk_level, [])

    if not candidates:
        return {
            "recommended_mitigation": None,
            "confidence": 0,
            "level": risk_level,
        }

    records = []
    for strategy in candidates:
        record = (
            db.query(MitigationStrategy)
            .filter(
                MitigationStrategy.tenant_id == tenant_id,
                MitigationStrategy.level == risk_level,
                MitigationStrategy.strategy == strategy,
            )
            .first()
        )

        if not record:
            record = MitigationStrategy(
                tenant_id=tenant_id,
                level=risk_level,
                strategy=strategy,
                total_plays=0,
                total_reward=0.0,
                average_reward=0.0,
            )
            db.add(record)
            # Commit is handled at a higher level.
            db.flush()

        records.append(record)

    # 2. Exploration
    if random.random() < EXPLORATION_RATE:
        chosen = random.choice(records)
        return {
            "recommended_mitigation": chosen.strategy,
            "confidence": 0.5,
            "level": risk_level,
        }

    # 3. Exploitation
    best = sorted(
        records,
        key=lambda s: (s.average_reward, -s.total_plays),
        reverse=True,
    )[0]

    return {
        "recommended_mitigation": best.strategy,
        "confidence": round(best.average_reward, 3),
        "level": risk_level,
    }

def resolve_decay(volatility_score: float| None)-> float:
    if volatility_score is None:
        return  0.9
    if volatility_score > 0.6:
        return 0.8
    elif volatility_score < 0.2:
        return 0.95
    else:
        return 0.9
    
@require_engine_version
def update_strategy_reward(
    db: Session,
    tenant_id: str,
    strategy: str,
    reward: float,
):
    record = (
        db.query(MitigationStrategy)
        .filter(
            MitigationStrategy.tenant_id == tenant_id,
            MitigationStrategy.strategy == strategy,
        )
        .first()
    )

    if not record:
        return
    
    forecast = predict_risk_horizon(db, tenant_id, horizon=5)
    volatility = forecast.get("volatility_score")
    
    if volatility is None:
        volatility = compute_volatility(db, tenant_id)

    if reward > 0:
        record.success_count += 1
    else:
        record.failure_count += 1

    context = "volatile" if volatility and volatility > 0.6 else "stable"
    if context == "volatile":
        if reward > 0:
            record.success_volatility += 1
        else:
            record.failure_volatility += 1
    else:
        if reward > 0:
            record.success_table += 1
        else:
            record.failure_table += 1

    decay = resolve_decay(volatility)
    record.total_plays += 1
    record.total_reward += reward
    record.average_reward = (
        decay * record.average_reward
        + (1 - decay) * reward
    )

    total_sample = (
        (record.success_table or 0) +
        (record.failure_table or 0) +
        (record.success_volatility or 0) +
        (record.failure_volatility or 0)
    )
    total_success = (
        (record.success_table or 0) +
        (record.success_volatility or 0)
    )
    total_failure = (
        (record.failure_stable or 0)+
        (record.failure_volatile or 0)
    )
    total_sample = total_success + total_failure

    if total_sample >= 20:
        lcb = beta_lower_bound(total_success, total_failure, confidence = 0.95)
        print(f"[RETIRE_CHECK]{record.strategy} LCB={round(lcb,4)}")

        if lcb < 0.20:
            print(f"⚠ Retiring {record.strategy} (Bayesian confidence)")
            record.is_active = False
            record.retired_at = datetime.utcnow()

    # Commit is handled at a higher level.
    db.flush()

def attemp_reactivation(db, tenant_id):
    forecast = predict_risk_horizon(db, tenant_id, horizon = 5)
    volatility = forecast.get("volatility_score")

    if volatility and volatility > 0.7 :
        retired = db.query(MitigationStrategy).filter(
            MitigationStrategy.tenant_id == tenant_id,
            MitigationStrategy.is_active == False
        ).all()

        for s in retired:
            print(f"Reactivating {s.strategy} due to high volatility")
            s.is_active = True
            s.retired_at = None

        # Commit is handled at a higher level.
        db.flush()    
