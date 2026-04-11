import random
from app.models.strategy_performance import StrategyPerformance

EXPLORATION_RATE = 0.05

LEVEL_STRATEGY_MAP = {
    "advisory": [
        "advisory_notice",
        "advisory_email",
        "compliance_reminder",
    ],
    "active": [
        "warning_flag",
        "temporary_restriction",
    ],
    "aggressive": [
        "suspension",
    ],
}

def apply_bandit_strategy(db, tenant_id, current_strategy, level):
    explore = random.random() < EXPLORATION_RATE

    if not explore:
        return {
            "strategy": current_strategy,
            "mode": "exploit"
        }

    possible_strategies = LEVEL_STRATEGY_MAP.get(level, [])

    alternatives = [
        s for s in possible_strategies if s != current_strategy
    ]

    if not alternatives:
        return {
            "strategy": current_strategy,
            "mode": "exploit"
        }

    chosen = random.choice(alternatives)

    return {
        "strategy": chosen,
        "mode": "explore"
    }
