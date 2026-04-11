from datetime import datetime, timedelta
from threading import RLock
from typing import Dict, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.system_event import SystemEvent
from app.models.tenant_policy import TenantPolicy
from app.models.tenant_risk_state import TenantRiskState
from app.services.adaptive_policy_engine import (
    BehaviorSnapshot,
    ESCALATED_POLICY,
    MitigationPolicy,
    NORMAL_POLICY,
    STRICT_POLICY,
    get_active_policy,
    refresh_policy_from_snapshot,
)

_policy_cache: Dict[str, MitigationPolicy] = {}
_lock = RLock()

_RISK_SCORE_MAX = 10.0
_REPEAT_WINDOW_DAYS = 7
_REPEAT_EVENT_NORMALIZER = 5.0
_REPEAT_EVENT_TYPES = ("risk_escalated", "tenant_quarantined")


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_behavior_snapshot(db: Session, tenant_id: str) -> BehaviorSnapshot:
    state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .first()
    )

    risk_score = float((state.risk_score if state else 0.0) or 0.0)
    risk_index = _clamp_01(risk_score / _RISK_SCORE_MAX)

    window_start = datetime.utcnow() - timedelta(days=_REPEAT_WINDOW_DAYS)
    repeat_events = (
        db.query(func.count(SystemEvent.id))
        .filter(SystemEvent.tenant_id == tenant_id)
        .filter(SystemEvent.created_at >= window_start)
        .filter(SystemEvent.event_type.in_(_REPEAT_EVENT_TYPES))
        .scalar()
    ) or 0

    repeat_offense_score = _clamp_01(float(repeat_events) / _REPEAT_EVENT_NORMALIZER)

    return BehaviorSnapshot(
        tenant_id=tenant_id,
        risk_index=risk_index,
        repeat_offense_score=repeat_offense_score,
    )


def load_policy_from_db(tenant_id: str) -> MitigationPolicy:
    db: Session = SessionLocal()

    try:
        record = db.query(TenantPolicy).filter_by(
            tenant_id=tenant_id
        ).first()

        if not record:
            return get_active_policy(tenant_id)

        # Rehydrate the persisted policy name into a concrete policy object.
        policy_map = {
            "NORMAL": NORMAL_POLICY,
            "ESCALATED": ESCALATED_POLICY,
            "STRICT": STRICT_POLICY,
        }
        policy = policy_map.get(record.policy_name, NORMAL_POLICY)

        with _lock:
            _policy_cache[tenant_id] = policy

        return policy

    finally:
        db.close()


def get_runtime_policy(tenant_id: str) -> MitigationPolicy:
    with _lock:
        if tenant_id in _policy_cache:
            return _policy_cache[tenant_id]

    return load_policy_from_db(tenant_id)


# =========================================================
# Policy Update Pipeline
# =========================================================

def update_policy_from_snapshot(snapshot: BehaviorSnapshot):
    new_policy = refresh_policy_from_snapshot(snapshot)

    db: Session = SessionLocal()

    try:
        record = db.query(TenantPolicy).filter_by(
            tenant_id=snapshot.tenant_id
        ).first()

        payload = {
            "source": "computed_snapshot",
            "risk_index": snapshot.risk_index,
            "repeat_score": snapshot.repeat_offense_score,
        }

        if not record:
            record = TenantPolicy(
                tenant_id=snapshot.tenant_id,
                policy_name=new_policy.name,
                reason_snapshot=payload,
            )
            db.add(record)

        else:
            record.policy_name = new_policy.name
            record.reason_snapshot = payload

        db.commit()

        with _lock:
            _policy_cache[snapshot.tenant_id] = new_policy

    finally:
        db.close()

    return new_policy


def refresh_policy_for_tenant(tenant_id: str) -> Tuple[MitigationPolicy, BehaviorSnapshot]:
    db: Session = SessionLocal()

    try:
        snapshot = compute_behavior_snapshot(db, tenant_id)
    finally:
        db.close()

    policy = update_policy_from_snapshot(snapshot)
    return policy, snapshot


# =========================================================
# Cache Maintenance
# =========================================================

def invalidate_policy_cache(tenant_id: str):
    with _lock:
        _policy_cache.pop(tenant_id, None)
