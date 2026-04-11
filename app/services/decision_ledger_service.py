from app.models.decision_snapshot import DecisionSnapshot
from app.services.ledger_utils import compute_hash
from app.core.engine_config import ENGINE_VERSION
from app.core.governance_guard import require_engine_version
import json


@require_engine_version
def write_decision_snapshot(
    db,
    tenant_id: str,
    risk_level: str,
    context: str,
    strategy_stats: list,
    selected_strategy: str,
    regret: float,
    random_seed: str,
):

    # Get previous hash
    last = (
        db.query(DecisionSnapshot)
        .filter(DecisionSnapshot.tenant_id == tenant_id)
        .order_by(DecisionSnapshot.created_at.desc())
        .first()
    )

    previous_hash = last.current_hash if last else "GENESIS"

    strategy_stats_json = json.dumps(strategy_stats)

    payload = (
        f"{tenant_id}"
        f"{risk_level}"
        f"{context}"
        f"{strategy_stats_json}"
        f"{selected_strategy}"
        f"{regret}"
        f"{random_seed}"
        f"{previous_hash}"
    )

    current_hash = compute_hash(payload)

    snapshot = DecisionSnapshot(
        tenant_id=tenant_id,
        risk_level=risk_level,
        context=context,
        strategy_stats_json=strategy_stats_json,
        selected_strategy=selected_strategy,
        regret=regret,
        random_seed=random_seed,
        engine_version=ENGINE_VERSION,
        previous_hash=previous_hash,
        current_hash=current_hash,
    )

    db.add(snapshot)
    # Commit is handled at a higher level.
