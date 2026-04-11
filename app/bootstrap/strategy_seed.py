from sqlalchemy.orm import Session
from app.models.mitigation_strategy import MitigationStrategy

STRATEGY_MAP = {
    "advisory": ["advisory_notice", "monitor"],
    "active": ["warning", "rate_limit"],
    "aggressive": ["full_restriction", "lockdown"],
}


def seed_strategies_for_tenant(db: Session, tenant_id: str):
    for level, strategies in STRATEGY_MAP.items():
        for strategy_name in strategies:

            exists = db.query(MitigationStrategy).filter(
                MitigationStrategy.tenant_id == tenant_id,
                MitigationStrategy.level == level,
                MitigationStrategy.strategy == strategy_name
            ).first()

            if not exists:
                db.add(
                    MitigationStrategy(
                        tenant_id=tenant_id,
                        level=level,
                        strategy=strategy_name,
                        total_plays=0,
                        total_reward=0.0,
                        average_reward=0.0
                    )
                )

    db.commit()