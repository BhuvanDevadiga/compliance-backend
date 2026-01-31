from datetime import datetime, timedelta

def detect_usage_spike(
    *,
    tenant_id: str,
    recent_count: int,
    baseline_per_minute: int,
):
    """
    Simple spike detection:
    if traffic >= 5x normal rate → anomaly
    """
    if recent_count >= baseline_per_minute * 5:
        _log_anomaly(
            tenant_id,
            recent_count,
            baseline_per_minute,
        )


def _log_anomaly(tenant_id, recent, baseline):
    print(
        f"🚨 ABUSE ANOMALY "
        f"tenant={tenant_id} "
        f"recent/min={recent} "
        f"baseline/min={baseline}"
    )
