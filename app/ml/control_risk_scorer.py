import math
from datetime import UTC, datetime

W_STALENESS = 0.35
W_OWNER_ACTIVITY = 0.25
W_HISTORY = 0.35
W_AUDIT_PROXIMITY = 0.05


def normalize_days(days, max_days=90):
    return max(0.0, min(days / max_days, 1.0))


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def _days_since(value, now):
    if value is None:
        return 90
    return max((now - value).days, 0)


def _audit_urgency(next_audit_date, now):
    if next_audit_date is None:
        return 0.0

    days_to_audit = (next_audit_date - now).days
    return 1 - normalize_days(max(days_to_audit, 0), max_days=1800)


def compute_control_failure_probability(control):
    now = datetime.now(UTC).replace(tzinfo=None)

    days_stale = _days_since(getattr(control, "last_evidence_updated_at", None), now)
    staleness_score = normalize_days(days_stale)

    days_owner_idle = _days_since(getattr(control, "owner_last_login", None), now)
    owner_score = normalize_days(days_owner_idle)

    history_score = getattr(control, "historical_failure_rate", 0.0) or 0.0
    history_score = max(0.0, min(history_score, 1.0))

    audit_urgency = _audit_urgency(getattr(control, "next_audit_date", None), now)

    raw_score = (
        W_STALENESS * staleness_score +
        W_OWNER_ACTIVITY * owner_score +
        W_HISTORY * history_score +
        W_AUDIT_PROXIMITY * audit_urgency
    )

    probability = sigmoid((raw_score - 0.50) * 6)
    return round(probability, 4)
