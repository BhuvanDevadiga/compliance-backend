from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.request_audit_log import RequestAuditLog
from app.models.tenant_profile import TenantProfile
from app.services.alert_engine import emit_intelligent_alert
from app.services.event_service import emit_event
from app.services.adaptive_risk_engine import escalate_risk
from app.services.intelligent_alerts import intelligent_alert





# Thresholds for profile-based anomalies
PROFILE_THRESHOLDS = {
    "request_rate": 10,        # max allowed requests per 5 min window
    "avg_latency_ms": 300,     # ms
    "error_ratio": 0.2,        # 20% errors
    "endpoint_hit": 50         # max hits per endpoint
}


def detect_anomalies(db: Session, tenant_id: str):
    """
    Detect anomalies using both raw audit logs and tenant profile metrics.
    Emits structured events on anomalies.
    """

    window = datetime.utcnow() - timedelta(minutes=5)

    # -------------------
    # Recent audit logs
    # -------------------
    recent_logs = (
        db.query(RequestAuditLog)
        .filter(
            RequestAuditLog.tenant_id == tenant_id,
            RequestAuditLog.created_at >= window,
        )
        .all()
    )

    if recent_logs:
        # Rule 1: Request spike
        if len(recent_logs) > 100:

            intelligent_alert(
                db=db,
                alert_key=f"anomaly_request_spike_{tenant_id}",
                event_type="anomaly_request_spike",
                tenant_id=tenant_id,
                payload={"count": len(recent_logs)},   
            )
            escalate_risk(db, tenant_id, "request_spike", severity=2.0)

        # Rule 2: Error burst
        errors = [r for r in recent_logs if r.status_code >= 500]
        if len(errors) > 10:
            intelligent_alert(
                db=db,
                alert_key=f"anomaly_error_burst_{tenant_id}",
                event_type="anomaly_error_burst",
                tenant_id=tenant_id,
                payload={"errors": len(errors)},
            )
            escalate_risk(db, tenant_id, "error_burst", severity=3.0)

        # Rule 3: Slow responses
        slow = [r for r in recent_logs if (r.latency_ms or 0) > 1000]
        if len(slow) > 5:
            intelligent_alert(
                db=db,
                alert_key=f"anomaly_latency_spike_{tenant_id}",
                event_type="anomaly_latency_spike",
                tenant_id=tenant_id,
                payload={"slow_requests": len(slow)},
            )
            escalate_risk(db, tenant_id, "latency_spike", severity=1.0)

    # -------------------
    # Tenant profile metrics
    # -------------------
    profile = db.query(TenantProfile).filter_by(tenant_id=tenant_id).first()
    if profile:
        # High request rate
        if profile.request_rate > PROFILE_THRESHOLDS["request_rate"]:
            intelligent_alert(
                db=db,
                alert_key=f"anomaly_profile_request_rate_{tenant_id}",
                event_type="anomaly_profile_request_rate",
                tenant_id=tenant_id,
                payload={"request_rate": profile.request_rate},        
          )
           

        # High average latency
        if profile.avg_latency_ms > PROFILE_THRESHOLDS["avg_latency_ms"]:
            intelligent_alert(
                db=db,
                alert_key=f"anomaly_profile_latency_{tenant_id}",
                event_type="anomaly_profile_latency",
                tenant_id=tenant_id,
                payload={"avg_latency_ms": profile.avg_latency_ms},
            )

        # High error ratio
        if profile.error_ratio > PROFILE_THRESHOLDS["error_ratio"]:
            intelligent_alert(
                db=db,
                alert_key=f"anomaly_profile_error_ratio_{tenant_id}",
                event_type="anomaly_profile_error_ratio",
                tenant_id=tenant_id,
                payload={"error_ratio": profile.error_ratio},
            )

        # Endpoint hit anomaly
        for endpoint, hits in (profile.endpoint_distribution or {}).items():
            if hits > PROFILE_THRESHOLDS["endpoint_hit"]:
                intelligent_alert(
                    db=db,
                    alert_key=f"anomaly_profile_endpoint_{tenant_id}_{endpoint}",
                    event_type="anomaly_profile_endpoint",
                    tenant_id=tenant_id,
                    payload={"endpoint": endpoint, "hits": hits},
                )
