from datetime import date


_fired_alerts = set()



def maybe_fire_quota_alert(
    *,
    tenant_id: str,
    plan: str,
    daily_limit: int,
    used_today: int,
):
    today = date.today()

    usage_pct = (used_today / daily_limit) * 100

    if usage_pct >= 100:
        _fire_once(tenant_id, today, "100%", plan, used_today, daily_limit)

    elif usage_pct >= 80:
        _fire_once(tenant_id, today, "80%", plan, used_today, daily_limit)


def _fire_once(tenant_id, today, level, plan, used, limit):
    key = (tenant_id, today, level)

    if key in _fired_alerts:
        return

    _fired_alerts.add(key)

    
    print(
        f"🚨 QUOTA ALERT [{level}] "
        f"tenant={tenant_id} "
        f"plan={plan} "
        f"used={used}/{limit}"
    )
