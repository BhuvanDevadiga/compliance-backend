def detect_usage_spike(
    *,
    tenant_id: str,
    recent_count: int,
    baseline_per_minute: int,
):
    if recent_count > baseline_per_minute * 3:
        print(
            f"🚨 ABUSE SPIKE "
            f"tenant={tenant_id} "
            f"recent={recent_count} "
            f"baseline={baseline_per_minute}/min"
        )
