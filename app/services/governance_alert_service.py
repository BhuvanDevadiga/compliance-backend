from app.models.governance_alert import GovernanceAlert
from datetime import datetime, timedelta
from sqlalchemy import desc

ALERT_DEDUP_WINDOW_SECONDS = 300

def create_alert(db, tenant_id: str, alert_type: str, severity: str, message: str):
    window_start = datetime.utcnow() - timedelta(seconds=ALERT_DEDUP_WINDOW_SECONDS)

    # Check for recent alert of same type
    existing_alert = (
        db.query(GovernanceAlert)
        .filter(
            GovernanceAlert.tenant_id == tenant_id,
            GovernanceAlert.alert_type == alert_type,
            GovernanceAlert.created_at >= window_start
        )
        .order_by(desc(GovernanceAlert.created_at))
        .first()
    )

    if existing_alert:
        # Escalation logic
        severity_order = ["info", "warning", "high", "critical"]

        try:
            current_index = severity_order.index(existing_alert.severity)
        except ValueError:
            current_index = 0

        # escalate by one level if not already critical
        if current_index < len(severity_order) - 1:
            existing_alert.severity = severity_order[current_index + 1]

        # Reopen if previously resolved
        existing_alert.status = "active"
        existing_alert.resolved_at = None

        return  # Do not create duplicate

    # Create new alert
    alert = GovernanceAlert(
        tenant_id=tenant_id,
        alert_type=alert_type,
        severity=severity,
        message=message,
    )

    db.add(alert)
