from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.request_audit_log import RequestAuditLog
from app.models.system_event import SystemEvent
from app.models.tenant_profile import TenantProfile
from datetime import datetime, timedelta
from app.services.drift_detector import detect_behavior_drift


WINDOW_MINUTES = 10


def generate_profile(db: Session, tenant_id: str):

    window_start = datetime.utcnow() - timedelta(minutes=WINDOW_MINUTES)

    events = (
        db.query(SystemEvent)
        .filter(SystemEvent.created_at >= window_start)
        .filter(SystemEvent.event_type == "risk_score_generated")
        .all()
    )

    print(f"Profiler found {len(events)} events")

    if not events:
        return

    scores = []
    endpoints = {}
    error_count = 0

    for e in events:
        payload = e.payload or {}

        score = payload.get("risk_score")
        endpoint = payload.get("endpoint")
        risk_level = payload.get("risk_level")

        if score is not None:
            scores.append(score)

        if endpoint:
            endpoints[endpoint] = endpoints.get(endpoint, 0) + 1

            if risk_level == "high":
                error_count += 1

    avg_score = sum(scores) / len(scores) if scores else 0
    request_rate = len(events) / WINDOW_MINUTES
    error_ratio = error_count / len(events) if events else 0

    audit_logs = (
    db.query(RequestAuditLog)
    .filter(RequestAuditLog.created_at >= window_start)
    .filter(RequestAuditLog.latency_ms.isnot(None))
    .all()
)
    latencies = [a.latency_ms for a in audit_logs]

    avg_latency = (
    sum(latencies) / len(latencies)
    if latencies
    else None
)

   
    profile = TenantProfile(
        tenant_id=tenant_id,
        avg_risk_score=avg_score,
        request_rate=request_rate,
        endpoint_distribution=endpoints,
        avg_latency_ms=avg_latency,
         error_ratio=error_ratio,
    )

    db.add(profile)
    # Commit is handled at a higher level.
    db.flush()
    detect_behavior_drift(db, tenant_id)


    print("✅ Profile snapshot saved")
