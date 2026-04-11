import logging

logger = logging.getLogger("alerts")


def dispatch_alert(event_type: str, tenant_id: str, payload: dict):
    """
    Central alert router.
    Extend later for webhooks / messaging / monitoring.
    """

    logger.warning(
        f"[ALERT] {event_type} | tenant={tenant_id} | payload={payload}"
    )

    # future hooks:
    # send_webhook(...)
    # push_to_queue(...)
    # notify_admin(...)
