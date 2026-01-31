from datetime import date
import logging

logger = logging.getLogger("app")

_fired = set()


def maybe_fire_quota_alert(
    *,
    tenant_id: str,
    plan: str,
    daily_limit: int,
    used_today: int,
):
    today = date.today()
    pct = int((used_today / daily_limit) * 100)

    if pct >= 100:
        _emit("100%", tenant_id, plan, used_today, daily_limit, today)
    elif pct >= 80:
        _emit("80%", tenant_id, plan, used_today, daily_limit, today)


def _emit(level, tenant_id, plan, used, limit, today):
    key = (tenant_id, today, level)
    if key in _fired:
        return

    _fired.add(key)

    logger.warning(
        "quota_alert",
        extra={
            "event": "quota_alert",
            "threshold": level,
            "tenant_id": tenant_id,
            "plan": plan,
            "used": used,
            "limit": limit,
        },
    )
