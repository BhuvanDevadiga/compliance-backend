from sqlalchemy.orm import Session
from app.models.decision_feedback import DecisionFeedback
from app.models.mitigation_strategy import MitigationStrategy
from app.models.decision_trace import DecisionTrace

DECAY = 0.9
STRATEGY_LEVEL_MAP = {
    "advisory_notice": "advisory",
    "monitor": "advisory",
    "warning": "active",
    "rate_limit": "active",
    "temporary_block": "aggressive",
    "full_restriction": "aggressive",
}
RISK_WEIGHTS = {
    "advisory": 1.0,
    "active": 1.5,
    "aggressive": 2.0,
}


def record_feedback(db: Session, decision_id: int, tenant_id: str, outcome: str):

    outcome = outcome.lower().strip()

    reward_map = {
        "success": 1.0,
        "failure": 0.0,
        "false_positive": -1.0,
    }

    base_reward = reward_map.get(outcome, 0)

    # Get mitigation used in that decision.
    decision = db.query(DecisionTrace).filter(
        DecisionTrace.id == decision_id,
        DecisionTrace.tenant_id == tenant_id,
    ).first()

    if not decision:
        return {
            "decision_id": decision_id,
            "outcome": outcome,
            "reward": base_reward,
            "updated": False,
            "reason": "decision_not_found_for_tenant",
        }

    # Prefer pre_mitigation for learning selected strategy performance.
    strategy_name = (
        getattr(decision, "pre_mitigation", None)
        or getattr(decision, "final_mitigation", None)
        or getattr(decision, "mitigation_action", None)
        or "none"
    )
    strategy_level = STRATEGY_LEVEL_MAP.get(strategy_name)
    weight = RISK_WEIGHTS.get(strategy_level, 1.0)
    reward = base_reward * weight

    feedback = DecisionFeedback(
        decision_id=decision_id,
        tenant_id=tenant_id,
        outcome=outcome,
        reward=reward,
    )

    db.add(feedback)

    query = db.query(MitigationStrategy).filter(
        MitigationStrategy.tenant_id == tenant_id,
        MitigationStrategy.strategy == strategy_name,
    )
    if strategy_level:
        strategy = query.filter(
            MitigationStrategy.level == strategy_level
        ).first()
    else:
        strategy = query.first()

    if not strategy:
        strategy = MitigationStrategy(
            tenant_id=tenant_id,
            level=strategy_level,
            strategy=strategy_name,
            total_plays=0,
            total_reward=0.0,
            average_reward=0.0,
            success_count=0,
            failure_count=0,
        )
        db.add(strategy)

    # Update stats.
    strategy.total_plays += 1
    strategy.total_reward += reward
    strategy.average_reward = (
        DECAY * strategy.average_reward
        + (1 - DECAY) * reward
    )
    if reward > 0:
        strategy.success_count += 1
    else:
        strategy.failure_count += 1

    db.commit()

    return {
        "decision_id": decision_id,
        "outcome": outcome,
        "reward": reward,
        "updated": True,
        "strategy": strategy_name,
        "level": strategy.level,
        "average_reward": strategy.average_reward,
        "total_plays": strategy.total_plays,
    }
