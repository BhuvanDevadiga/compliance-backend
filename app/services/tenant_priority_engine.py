from app.models.behavior_memory import BehaviorMemory


def classify_tenant_priority(db, tenant_id: str):
    """
    Determines scheduler cadence based on recent behavior severity.
    """

    history = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(5)
        .all()
    )

    if not history:
        return "stable"

    critical = sum(
        1 for h in history if h.classification == "critical behavior"
    )

    if critical >= 3:
        return "critical"

    if critical >= 1:
        return "elevated"

    return "stable"


def resolve_cycle_interval(priority: str):
    """
    Maps tenant priority to scheduler interval.
    """

    return {
        "critical": 30,
        "elevated": 60,
        "stable": 120,
    }.get(priority, 60)
