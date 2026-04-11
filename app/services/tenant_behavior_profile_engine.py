from sqlalchemy.orm import Session

from app.models.tenant_behavior_profile import TenantBehaviorProfile
from app.services.mitigation_learning_tuner import (
    tune_mitigation_strategy,
)


def update_tenant_profile(db: Session, tenant_id: str):
    """
    Applies learning feedback to persistent tenant profile.
    """

    learning = tune_mitigation_strategy(db, tenant_id)

    profile = (
        db.query(TenantBehaviorProfile)
        .filter(TenantBehaviorProfile.tenant_id == tenant_id)
        .first()
    )

    if not profile:
        profile = TenantBehaviorProfile(tenant_id=tenant_id)
        db.add(profile)

    profile.escalation_bias = profile.escalation_bias if profile.escalation_bias is not None else 0
    profile.stability_score = profile.stability_score if profile.stability_score is not None else 0.5

    # update bias
    profile.escalation_bias += learning["adjustment"]

    # stabilize bounds
    profile.escalation_bias = max(-3, min(3, profile.escalation_bias))

    # adjust stability score
    if learning["learning"] == "strong_success":
        profile.stability_score += 0.05
    elif learning["learning"] == "failure":
        profile.stability_score -= 0.05

    profile.stability_score = max(0.1, min(1.0, profile.stability_score))

    # Commit is handled at a higher level.
    db.flush()

    return {
        "tenant": tenant_id,
        "profile_bias": profile.escalation_bias,
        "stability": profile.stability_score,
    }
