from sqlalchemy.orm import Session
from app.models.mitigation_strategy_performance import MitigationStrategyPerformance
from app.services.mitigation_feedback_engine import evaluate_mitigation_effectiveness


def update_strategy_performance(db: Session, tenant_id: str, strategy: str | None = None):
    effectiveness = evaluate_mitigation_effectiveness(db, tenant_id)
    learning = effectiveness["learning"]
    strategy_name = strategy or "unknown"

    record = (
        db.query(MitigationStrategyPerformance)
        .filter(
            MitigationStrategyPerformance.tenant_id == tenant_id,
            MitigationStrategyPerformance.strategy == strategy_name,
        )
        .first()
    )

    if not record:
        record = MitigationStrategyPerformance(
            tenant_id=tenant_id,
            strategy=strategy_name,
            success_score=1.0,
            failure_score=1.0,
            short_term_success=0.0,
            short_term_failure=0.0,
            confidence=1.0,
        )
        db.add(record)

    if record.success_score is None:
        record.success_score = 1.0
    if record.failure_score is None:
        record.failure_score = 1.0
    if record.confidence is None:
        record.confidence = 1.0
    if record.short_term_success is None:
        record.short_term_success = 0.0
    if record.short_term_failure is None:
        record.short_term_failure = 0.0        
    
    if learning in ["strong_success", "mild_success"]:
        record.success_score += 1
        record.short_term_success += 1
    else:
        record.failure_score += 1
        record.short_term_failure += 1

    long_total = record.success_score + record.failure_score
    long_conf = (
    record.success_score / long_total
    if long_total > 0 else 0.0
    )
    short_total = record.short_term_success + record.short_term_failure
    short_conf = (
    record.short_term_success / short_total
    if short_total > 0 else 0.0
    )
    record.confidence = (
    0.7 * long_conf +
    0.3 * short_conf
    )

    # Commit is handled at a higher level.
    db.flush()

    return {
        "tenant_id": tenant_id,
        "strategy": strategy_name,
        "learning": learning,
        "success_score": record.success_score,
        "failure_score": record.failure_score,
        "short_term_success": record.short_term_success,
        "short_term_failure": record.short_term_failure,
        "confidence": record.confidence,
    }
