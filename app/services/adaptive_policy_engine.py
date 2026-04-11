"""
Adaptive Policy Engine

Converts tenant behavior intelligence snapshots into
runtime mitigation policies.

Design goals:
- deterministic policy selection
- lightweight in-memory cache
- extensible thresholds
- safe fallback behavior
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Dict, Optional


# =========================================================
# Policy Definitions
# =========================================================

@dataclass(frozen=True)
class MitigationPolicy:
    name: str
    rate_limit_multiplier: float
    quarantine_threshold: float
    alert_sensitivity: float
    mitigation_cooldown_seconds: int


NORMAL_POLICY = MitigationPolicy(
    name="NORMAL",
    rate_limit_multiplier=1.0,
    quarantine_threshold=0.85,
    alert_sensitivity=1.0,
    mitigation_cooldown_seconds=60,
)

ESCALATED_POLICY = MitigationPolicy(
    name="ESCALATED",
    rate_limit_multiplier=0.6,
    quarantine_threshold=0.70,
    alert_sensitivity=1.3,
    mitigation_cooldown_seconds=120,
)

STRICT_POLICY = MitigationPolicy(
    name="STRICT",
    rate_limit_multiplier=0.3,
    quarantine_threshold=0.55,
    alert_sensitivity=1.6,
    mitigation_cooldown_seconds=240,
)


# =========================================================
# Snapshot Contract (minimal expectation)
# =========================================================

class BehaviorSnapshot:
    """
    Expected snapshot interface.
    Adapt to your real model if needed.
    """

    def __init__(
        self,
        tenant_id: str,
        risk_index: float,
        repeat_offense_score: float,
        timestamp: Optional[datetime] = None,
    ):
        self.tenant_id = tenant_id
        self.risk_index = risk_index
        self.repeat_offense_score = repeat_offense_score
        self.timestamp = timestamp or datetime.utcnow()


# =========================================================
# Policy Cache
# =========================================================

_policy_cache: Dict[str, MitigationPolicy] = {}
_cache_lock = RLock()


def get_active_policy(tenant_id: str) -> MitigationPolicy:
    """
    Fast runtime lookup.
    Always returns a valid policy.
    """

    with _cache_lock:
        return _policy_cache.get(tenant_id, NORMAL_POLICY)


# =========================================================
# Core Decision Logic
# =========================================================

def compute_policy(snapshot: BehaviorSnapshot) -> MitigationPolicy:
    """
    Deterministic policy selection logic.

    Threshold tuning lives here.
    """

    risk = snapshot.risk_index
    repeat = snapshot.repeat_offense_score

    # Strict escalation
    if risk >= 0.80 or repeat >= 0.75:
        return STRICT_POLICY

    # Moderate escalation
    if risk >= 0.60 or repeat >= 0.50:
        return ESCALATED_POLICY

    # Default
    return NORMAL_POLICY


# =========================================================
# Policy Update Pipeline
# =========================================================

def update_policy(snapshot: BehaviorSnapshot) -> MitigationPolicy:
    """
    Compute + cache tenant policy.
    Handles drift detection.
    """

    new_policy = compute_policy(snapshot)

    with _cache_lock:
        old_policy = _policy_cache.get(snapshot.tenant_id)

        _policy_cache[snapshot.tenant_id] = new_policy

    # Drift logging hook
    if old_policy and old_policy.name != new_policy.name:
        _log_policy_transition(snapshot, old_policy, new_policy)

    return new_policy


# =========================================================
# Drift Logging Hook
# =========================================================

def _log_policy_transition(
    snapshot: BehaviorSnapshot,
    old_policy: MitigationPolicy,
    new_policy: MitigationPolicy,
):
    """
    Replace with DB logging or observability integration.
    """

    print(
        "[POLICY DRIFT]",
        f"tenant={snapshot.tenant_id}",
        f"{old_policy.name} -> {new_policy.name}",
        f"risk={snapshot.risk_index:.2f}",
        f"repeat={snapshot.repeat_offense_score:.2f}",
    )


# =========================================================
# Bulk Refresh (scheduler entry point)
# =========================================================

def refresh_policy_from_snapshot(snapshot: BehaviorSnapshot):
    """
    Public API used by behavior aggregator.
    """

    return update_policy(snapshot)
