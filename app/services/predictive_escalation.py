from statistics import mean


class EscalationPrediction:
    def __init__(self, tenant_id: str, score: float, reason: dict):
        self.tenant_id = tenant_id
        self.score = score
        self.reason = reason

    @property
    def should_escalate(self) -> bool:
        return self.score >= 0.75


def compute_risk_velocity(snapshots) -> float:
    if len(snapshots) < 2:
        return 0.0

    deltas = [
        snapshots[i].risk_index - snapshots[i - 1].risk_index
        for i in range(1, len(snapshots))
    ]
    return float(mean(deltas))


def compute_repeat_acceleration(snapshots) -> float:
    if len(snapshots) < 2:
        return 0.0

    deltas = [
        snapshots[i].repeat_offense_score - snapshots[i - 1].repeat_offense_score
        for i in range(1, len(snapshots))
    ]
    return float(mean(deltas))


def predict_escalation(tenant_id: str, snapshots):
    velocity = compute_risk_velocity(snapshots)
    repeat_accel = compute_repeat_acceleration(snapshots)

    raw_score = max(0.0, velocity * 1.5 + repeat_accel)
    score = min(1.0, raw_score)

    reason = {
        "risk_velocity": round(velocity, 3),
        "repeat_acceleration": round(repeat_accel, 3),
    }

    return EscalationPrediction(tenant_id, score, reason)
