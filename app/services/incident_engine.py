from sqlalchemy.orm import Session
from app.models.compliance_incident import ComplianceIncident
from datetime import datetime, timedelta


def create_incident(
    db,
    tenant_id: str,
    signal: str,
    health_delta: float,
    strict_ratio: float,
    governance_delta: float,
):

    cooldown_window = datetime.utcnow() - timedelta(minutes=30)

    existing = (
        db.query(ComplianceIncident)
        .filter(
            ComplianceIncident.tenant_id == tenant_id,
            ComplianceIncident.incident_type == signal,
            ComplianceIncident.detected_at >= cooldown_window
        )
        .first()
    )

    
    if existing:
        return

    severity = "low"

    if signal == "risk_spike":
        severity = "high"

    elif signal == "drift_alert":
        severity = "medium"

    elif signal == "mitigation_overuse":
        severity = "medium"

    elif signal == "governance_drop":
        severity = "high"

    incident = ComplianceIncident(
        tenant_id=tenant_id,
        incident_type=signal,
        severity=severity,
        health_delta=health_delta,
        strict_ratio=strict_ratio,
        governance_delta=governance_delta
    )

    db.add(incident)
    db.commit()