
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
from packaging import version
from app.core.engine_config import ENGINE_VERSION
from app.models.governance_alert import GovernanceAlert
from app.models.governance_event_log import GovernanceEventLog
from sqlalchemy.orm import Session
from app.models.governance_key import GovernanceKey
from app.services.tenant_state_service import get_tenant_state
from app.services.signing_service import compute_event_hash, sign_hash
from app.core.engine_config import GOVERNANCE_KEY_ID
from app.core.crypto_utils import decrypt_secret
from app.core.tenant_lock import acquire_tenant_lock
from app.services.governance_alert_service import create_alert
from app.services.adaptive_risk_engine import check_risk_escalation_burst
from sqlalchemy.sql import func

EVENT_SPIKE_WINDOW_SECONDS = 60
EVENT_SPIKE_THRESHOLD = 50


def check_event_spike(db, tenant_id: str, current_timestamp: datetime):
    if not tenant_id:
        return

    window_start = current_timestamp - timedelta(seconds=EVENT_SPIKE_WINDOW_SECONDS)

    recent_count = (
        db.query(func.count(GovernanceEventLog.id))
        .filter(
            GovernanceEventLog.tenant_id == tenant_id,
            GovernanceEventLog.created_at >= window_start
        )
        .scalar()
    )

    if recent_count and recent_count >= EVENT_SPIKE_THRESHOLD:
        create_alert(
            db=db,
            tenant_id=tenant_id,
            alert_type="event_spike_detected",
            severity="warning",
            message=(
                f"{recent_count} governance events in last "
                f"{EVENT_SPIKE_WINDOW_SECONDS} seconds"
            ),
        )


def log_governance_event(
    db,
    event_type: str,
    tenant_id: str = None,
    previous_version: str = None,
    new_version: str = None,
    reason: str = None,
):
    timestamp = datetime.now(UTC).replace(tzinfo=None)

    last_event = db.query(GovernanceEventLog)\
    .filter(GovernanceEventLog.tenant_id == tenant_id)\
    .order_by(GovernanceEventLog.created_at.desc())\
    .first()

    if not last_event:
        previous_hash = "GENESIS"
    else:
        previous_hash = last_event.event_hash

    payload = f"{event_type}|{tenant_id}|{reason}|{timestamp}"
    event_hash = compute_event_hash(payload, previous_hash)
    signature, signing_key_id = sign_hash(db, event_hash)

    event = GovernanceEventLog(
        tenant_id=tenant_id,
        event_type=event_type,
        previous_version=previous_version,
        new_version=new_version,
        reason=reason,
        created_at=timestamp,
        previous_hash=previous_hash,
        event_hash=event_hash,
        signature=signature,
        signing_key_id=signing_key_id,
        original_payload=payload,
    )
    
    db.add(event)
    # Ensure subsequent events in the same transaction see this event.
    db.flush()
    check_event_spike(db, tenant_id, timestamp)
    # Commit is handled at a higher level.

def backfill_missing_signing_key_ids(db: Session) -> int:
    events = db.query(GovernanceEventLog).filter(
        GovernanceEventLog.signing_key_id.is_(None)
    ).all()

    if not events:
        return 0

    keys = db.query(GovernanceKey).all()
    if not keys:
        return 0

    updated = 0
    for event in events:
        if not event.signature or not event.event_hash:
            continue

        for key in keys:
            secret = decrypt_secret(key.encrypted_secret)
            expected = hmac.new(
                secret.encode(),
                event.event_hash.encode(),
                hashlib.sha256
            ).hexdigest()
            if hmac.compare_digest(expected, event.signature):
                event.signing_key_id = key.key_id
                updated += 1
                break

    if updated:
        # Commit is handled at a higher level.
        db.flush()

    return updated


def attempt_auto_unfreeze(db: Session, tenant_id: str):
    
    state = get_tenant_state(db, tenant_id)

    if not state or not state.adaptive_engine_frozen:
        return False

    if not state.freeze_locked_version:
        return False

    if version.parse(ENGINE_VERSION) > version.parse(state.freeze_locked_version):

        previous_version = state.freeze_locked_version

        state.adaptive_engine_frozen = False
        state.freeze_reason = f"Unlocked via version bump to {ENGINE_VERSION}"
        state.freeze_locked_version = None
        state.frozen_at = None

        # Commit is handled at a higher level.
        db.flush()

        if db.in_transaction():
            tenant_state = acquire_tenant_lock(db, tenant_id)
            log_governance_event(
                db=db,
                event_type="UNLOCK",
                tenant_id=tenant_id,
                previous_version=previous_version,
                new_version=ENGINE_VERSION,
                reason="Version bump unlock",
            )
        else:
            with db.begin():
                tenant_state = acquire_tenant_lock(db, tenant_id)
                log_governance_event(
                    db=db,
                    event_type="UNLOCK",
                    tenant_id=tenant_id,
                    previous_version=previous_version,
                    new_version=ENGINE_VERSION,
                    reason="Version bump unlock",
                )

        return True

    return False

def log_ml_decision(
    db,
    tenant_id: str,
    instability_probability: float,
    exploration_multiplier: float,
    effective_exploration_rate: float,
    risk_score: float,
):
    if instability_probability > 0.7:
        reason = "High instability → reduce exploration"
    elif instability_probability < 0.3:
        reason = "Low instability → increase exploration"
    else:
        reason = "Stable → normal exploration"

    payload = (
    "ml_decision|"
    f"{tenant_id}|"
    f"{instability_probability:.6f}|"
    f"{exploration_multiplier:.6f}|"
    f"{effective_exploration_rate:.6f}|"
    f"{reason}"
    )

    previous_event = db.query(GovernanceEventLog)\
        .filter(GovernanceEventLog.tenant_id == tenant_id)\
        .order_by(GovernanceEventLog.created_at.desc())\
        .first()

    if not previous_event:
        previous_hash = "GENESIS"
    else:
        previous_hash = previous_event.event_hash

    event_hash = compute_event_hash(payload, previous_hash)

    signature, key_id = sign_hash(db, event_hash)

    new_event = GovernanceEventLog(
        event_type="ml_decision",
        tenant_id=tenant_id,
        reason=reason,
        event_hash=event_hash,
        previous_hash=previous_hash,
        signature=signature,
        signing_key_id=key_id,
        original_payload = payload,
    )

    db.add(new_event)
    db.flush()
    check_event_spike(db, tenant_id, datetime.now(UTC).replace(tzinfo=None))
    check_risk_escalation_burst(db, tenant_id, risk_score)

def create_governance_alert(db, tenant_id, score):
    alert = GovernanceAlert(
        tenant_id=tenant_id,
        alert_type="AUDIT_BEHAVIOR_ANOMALY",
        severity="HIGH",
        anomaly_score=float(score),
        created_at=datetime.now(UTC).replace(tzinfo=None)
    )
    db.add(alert)
    db.commit()



