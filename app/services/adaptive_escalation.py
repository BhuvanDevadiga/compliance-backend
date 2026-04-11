from statistics import mean

from sqlalchemy.orm import Session

from app.models.behavior_memory import BehaviorMemory


def compute_adaptive_threshold(
    db: Session,
    tenant_id: str,
    lookback: int = 20,
) -> int:
    """
    Compute tenant-specific escalation threshold.

    Lower threshold (more sensitive) when behavior is persistently risky.
    Raise threshold when behavior is consistently stable.
    """

    history = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(lookback)
        .all()
    )

    if not history:
        return 3

    scores = [float(h.behavior_score or 0.0) for h in history]
    avg_score = mean(scores)

    spike_count = sum(1 for h in history if h.volatility in {"spike", "chaotic"})
    spike_ratio = spike_count / len(history)

    if avg_score >= 0.8 or spike_ratio >= 0.4:
        return 2

    if avg_score <= 0.4 and spike_ratio <= 0.1:
        return 4

    return 3
