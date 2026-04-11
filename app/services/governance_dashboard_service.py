from datetime import datetime
from sqlalchemy.orm import Session
from app.models.system_state import GlobalSystemState
from app.models.governance_event_log import GovernanceEventLog
from app.services.risk_metrics_service import get_regret_risk_index
from app.services.instability_model import compute_instability_probability, get_instability_features

def get_governance_overview(db: Session):

    state = db.query(GlobalSystemState).first()

    # 📊 Risk metrics
    metrics = get_regret_risk_index(db)

    # 🧠 ML instability
    features = get_instability_features(metrics)
    instability = compute_instability_probability(**features)

    # 🎯 Exploration logic (same as bandit)
    if instability > 0.7:
        exploration_multiplier = 0.5
    elif instability < 0.3:
        exploration_multiplier = 1.2
    else:
        exploration_multiplier = 1.0

    BASE_EXPLORATION = 0.4
    effective_exploration = BASE_EXPLORATION * exploration_multiplier

    # 📜 Event stats
    total_events = db.query(GovernanceEventLog).count()

    last_event = db.query(GovernanceEventLog)\
        .order_by(GovernanceEventLog.created_at.desc())\
        .first()

    # 🔐 Chain integrity (light check)
    integrity_status = "UNKNOWN"
    try:
        from app.api.governance import verify_governance_integrity
        result = verify_governance_integrity(db)
        integrity_status = result.get("status", "UNKNOWN")
    except Exception:
        integrity_status = "ERROR"

    return {
        "engine_version": state.engine_version if hasattr(state, "engine_version") else "2.1.0",
        "freeze_status": state.adaptive_engine_frozen,
        "freeze_reason": state.freeze_reason,
        "override_active": state.platform_override_active,
        "override_reason": state.platform_override_reason,

        "regret_risk_index": metrics["regret_risk_index"],
        "risk_level": metrics["risk_level"],

        "instability": round(instability, 4),
        "exploration_rate": round(effective_exploration, 4),

        "total_events": total_events,
        "last_event": last_event.event_type if last_event else None,

        "chain_integrity": integrity_status,
        "evaluated_at": datetime.utcnow().isoformat()
    }
