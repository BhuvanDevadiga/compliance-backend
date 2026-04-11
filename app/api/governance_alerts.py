from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.core.auth import get_current_tenant
from app.models.governance_alert import GovernanceAlert
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func


router = APIRouter(
    prefix="/api/governance/alerts",
    tags=["Governance Alerts"],
)

# Backwards-compatible export for app/main.py imports.
governance_alerts = router


@router.get("/")
def list_alerts(
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    query = db.query(GovernanceAlert).filter(
        GovernanceAlert.tenant_id == tenant.tenant_id
    )

    if severity:
        query = query.filter(GovernanceAlert.severity == severity)

    alerts = (
        query.order_by(GovernanceAlert.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "tenant_id": tenant.tenant_id,
        "count": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at,
            }
            for a in alerts
        ],
    }

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    alert = db.query(GovernanceAlert).filter(
        GovernanceAlert.id == alert_id,
        GovernanceAlert.tenant_id == tenant.tenant_id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()

    return {"message": "Alert acknowledged"}

@router.post("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    alert = db.query(GovernanceAlert).filter(
        GovernanceAlert.id == alert_id,
        GovernanceAlert.tenant_id == tenant.tenant_id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()

    return {"message": "Alert resolved"}

@router.get("/metrics")
def alert_metrics(
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    base_query = db.query(GovernanceAlert).filter(GovernanceAlert.tenant_id==tenant.tenant_id, GovernanceAlert.status == "active")
    total_active = base_query.count()
    severity_counts = (
        db.query(
            GovernanceAlert.severity,
            func.count(GovernanceAlert.id)
        )
        .filter(
            GovernanceAlert.tenant_id == tenant.tenant_id,
            GovernanceAlert.status == "active"
        )
        .group_by(GovernanceAlert.severity)
        .all()
    )

    type_counts = (
        db.query(
            GovernanceAlert.alert_type,
            func.count(GovernanceAlert.id)
        )
        .filter(
            GovernanceAlert.tenant_id == tenant.tenant_id,
            GovernanceAlert.status == "active"
        )
        .group_by(GovernanceAlert.alert_type)
        .all()
    )

    return {
        "tenant_id": tenant.tenant_id,
        "active_alerts_total": total_active,
        "by_severity": {
            severity: count for severity, count in severity_counts
        },
        "by_type": {
            alert_type: count for alert_type, count in type_counts
        },
    } 


