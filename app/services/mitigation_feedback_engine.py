from sqlalchemy.orm import Session

from app.models.mitigation_outcome import MitigationOutcome
from app.models.mitigation_strategy_performance import MitigationStrategyPerformance
from app.services.mitigation_learning import (
    evaluate_mitigation_effectiveness as _evaluate_mitigation_effectiveness,
)


def record_mitigation_outcome(
    db: Session,
    tenant_id: str,
    mitigation_action: str,
    behavior_improved: bool,
):
    """
    Records whether mitigation improved tenant behavior.
    """

    outcome = MitigationOutcome(
        tenant_id=tenant_id,
        mitigation_action=mitigation_action,
        behavior_improved=behavior_improved,
    )

    db.add(outcome)
    db.commit()


def select_best_mitigation(
    db: Session,
    tenant_id: str,
    level: str,
):
   

    strategy_map = {
        "advisory": [
            "advisory_notice",
            "monitor",
        ],
        "active": [
            "rate_limit",
            "temporary_block",
        ],
        "aggressive": [
            "lockdown",
            "full_restriction",
        ],
    }

    return strategy_map.get(level, [])


def evaluate_mitigation_effectiveness(
    db: Session,
    tenant_id: str,
    window: int = 5,
):
    """
    Backward-compatible passthrough so existing imports from this module keep working.
    """
    return _evaluate_mitigation_effectiveness(db, tenant_id, window=window)


def update_mitigation_performance(
    db: Session,
    tenant_id: str,
    strategy: str,
    success: bool,
    auto_commit: bool = False,
):
    """
    Update per-strategy performance scores and record the outcome event.
    """
    record = (
        db.query(MitigationStrategyPerformance)
        .filter(
            MitigationStrategyPerformance.tenant_id == tenant_id,
            MitigationStrategyPerformance.strategy == strategy,
        )
        .first()
    )

    if not record:
        record = MitigationStrategyPerformance(
            tenant_id=tenant_id,
            strategy=strategy,
            success_score=1.0,
            failure_score=1.0,
            confidence=0.5,
        )
        db.add(record)

    if success:
        record.success_score += 1
    else:
        record.failure_score += 1

    total = record.success_score + record.failure_score
    record.confidence = record.success_score / total if total else 0.5

    db.add(
        MitigationOutcome(
            tenant_id=tenant_id,
            mitigation_action=strategy,
            behavior_improved=success,
        )
    )

    if auto_commit:
        db.commit()
    else:
        db.flush()

    return {
        "tenant_id": tenant_id,
        "strategy": strategy,
        "success_score": record.success_score,
        "failure_score": record.failure_score,
        "confidence": record.confidence,
    }
