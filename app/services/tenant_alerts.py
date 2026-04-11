from app.services.event_bus import emit_event


def evaluate_alerts(
    tenant_id: str,
    health_score: int,
    risk_level: str,
    quarantined: bool,
):
    """
    Emit admin alerts based on tenant state.
    """

    # Critical health alert
    if health_score < 40:
        emit_event(
            event_type="alert_health_critical",
            tenant_id=tenant_id,
            payload={"health_score": health_score},
        )

    # High risk alert
    if risk_level in ("high", "critical"):
        emit_event(
            event_type="alert_risk_high",
            tenant_id=tenant_id,
            payload={"risk_level": risk_level},
        )

    # Isolation alert
    if quarantined:
        emit_event(
            event_type="alert_tenant_isolated",
            tenant_id=tenant_id,
            payload={"status": "isolated"},
        )
