from sqlalchemy.orm import Session
from app.models.tenant_profile import TenantProfile
from app.services.event_bus import emit_event


DRIFT_THRESHOLDS = {
    "latency": 2.0,       # 2x increase
    "error_ratio": 1.5,   # 50% increase
    "request_rate": 2.0,
}


def detect_behavior_drift(db: Session, tenant_id: str):
    profiles = (
        db.query(TenantProfile)
        .filter(TenantProfile.tenant_id == tenant_id)
        .order_by(TenantProfile.created_at.desc())
        .limit(2)
        .all()
    )

    if len(profiles) < 2:
        return

    latest, previous = profiles

    drift_flags = []

    if previous.avg_latency_ms and latest.avg_latency_ms:

        if latest.avg_latency_ms > previous.avg_latency_ms * DRIFT_THRESHOLDS["latency"]:
            drift_flags.append("latency_spike")

    if previous.error_ratio and latest.error_ratio:
        if latest.error_ratio > previous.error_ratio * DRIFT_THRESHOLDS["error_ratio"]:
            drift_flags.append("error_spike")

    if previous.request_rate and latest.request_rate:
        if latest.request_rate > previous.request_rate * DRIFT_THRESHOLDS["request_rate"]:
            drift_flags.append("traffic_spike")

    if drift_flags:
        emit_event(
            event_type="behavior_drift_detected",
            tenant_id=tenant_id,
            payload={
                "drifts": drift_flags,
                "latest_profile": latest.id,
                "previous_profile": previous.id,
            },
        )
