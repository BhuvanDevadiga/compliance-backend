"""
Pre-emptive Policy Override Engine

Escalates tenant enforcement policy when predictive
signals indicate imminent risk.
"""

from app.services.adaptive_policy_engine import (
    BehaviorSnapshot,
    STRICT_POLICY,
    update_policy,
)


def trigger_preemptive_override(
    tenant_id: str,
    prediction,
):
    """
    Escalate tenant policy immediately
    based on prediction signal.
    """

    if not prediction.should_escalate:
        return None

    # synthetic high-risk snapshot
    snapshot = BehaviorSnapshot(
        tenant_id=tenant_id,
        risk_index=0.95,
        repeat_offense_score=0.9,
    )

    new_policy = update_policy(snapshot)

    print(
        "[PREEMPTIVE OVERRIDE]",
        tenant_id,
        "→",
        new_policy.name,
    )

    return new_policy
