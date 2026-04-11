from sqlalchemy.orm import Session

from app.services.tenant_behavior_scoring import compute_tenant_behavior_score


def evolve_tenant_policy(
    db: Session,
    tenant_id: str,
):
    """
    Converts tenant intelligence score into
    adaptive policy posture.
    """

    intelligence = compute_tenant_behavior_score(db, tenant_id)
    score = intelligence["score"]

    if intelligence["risk_level"] == "unknown":
        policy_mode = "NORMAL"

    elif score < 1.8:
        policy_mode = "RELAXED"

    elif score < 3:
        policy_mode = "NORMAL"

    else:
        policy_mode = "STRICT"

    return {
        "policy_mode": policy_mode,
        "tenant_score": intelligence,
    }
