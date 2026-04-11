from app.models.tenant_profile import TenantProfile
from app.models.tenant_behavior_profile import TenantBehaviorProfile

def update_adaptive_threshold(db, tenant_id):
    profile = db.query(TenantProfile).filter(
        TenantProfile.tenant_id == tenant_id
    ).first()

    if not profile:
        return None
    
    behavior_profile = (
        db.query(TenantBehaviorProfile)
        .filter(TenantBehaviorProfile.tenant_id == tenant_id)
        .first()
    )

    base = 0.55
    stability = (
        behavior_profile.stability_score
        if behavior_profile and behavior_profile.stability_score is not None
        else 0.5
    )
    bias = (
        behavior_profile.escalation_bias
        if behavior_profile and behavior_profile.escalation_bias is not None
        else 0
    )

    volatility = 1-stability

    new_threshold = (
        base
        + (stability * 0.1)
        - (volatility * 0.1)
        - (bias * 0.05)
    )

    new_threshold = max(0.3, min(0.8, new_threshold))

    profile.adaptive_threshold = new_threshold
    # Commit is handled at a higher level.
    db.flush()

    return {
        "tenant": tenant_id,
        "adaptive_threshold": new_threshold,
        "stability": stability,
        "volatility": volatility,
        "bias": bias,
    }
        

    

    
    
