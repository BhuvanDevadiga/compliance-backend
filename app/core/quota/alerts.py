from datetime import date

# In-memory dedupe (OK for local + testing)
# In prod → Redis / DB
_fired_alerts = set()


def maybe_fire_quota_alert(
    *,
    tenant_id: str,
    plan: str,
    daily_limit: int,
    used_today: int,
):
    """
    Fires quota alerts at 80% and 100%.
    Safe to call on every request.
    """

    # Defensive guards
    if daily_limit is None or daily_limit <= 0:
        return

    usage_pct = (used_today / daily_limit) * 100
    today = date.today()

    if usage_pct >= 100:
        _fire_once(
            tenant_id=tenant_id,
            today=today,
            level="100%",
            plan=plan,
            used=used_today,
            limit=daily_limit,
        )

    elif usage_pct >= 80:
        _fire_once(
            tenant_id=tenant_id,
            today=today,
            level="80%",
            plan=plan,
            used=used_today,
            limit=daily_limit,
        )


def _fire_once(
    *,
    tenant_id: str,
    today: date,
    level: str,
    plan: str,
    used: int,
    limit: int,
):
    

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
