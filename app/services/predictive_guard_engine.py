from app.models.behavior_memory import BehaviorMemory

def predictive_escalation_guard(
    db,
    tenant_id: str,
    window: int = 15,
):
    """
    Evaluates recent behavior to predict if escalation is likely.
    """

    history = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(window)
        .all()
    )

    if len(history) < window:
        return {
            "guard_triggered": "False",
            "reason": "insufficient history",
        }

    score = [h.behavior_score for h in reversed(history)]
    velocity = score[-1] - score[0]   
    guard_triggered = velocity >= 0.25

    return {
        "guard_triggered": guard_triggered,
        "velocity": round(velocity, 2),
        "score_trend": score,
        "window": window,
    }


# Backward-compatible alias for older imports/calls.
def predective_escalation_guard(db, tenant_id: str, window: int = 15):
    return predictive_escalation_guard(db, tenant_id, window)
