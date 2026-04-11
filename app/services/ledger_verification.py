
from app.models.decision_snapshot import DecisionSnapshot
from app.services.ledger_utils import compute_hash


def verify_ledger_chain(db, tenant_id: str) -> bool:
    
    snapshots = (
        db.query(DecisionSnapshot)
        .filter(DecisionSnapshot.tenant_id == tenant_id)
        .order_by(DecisionSnapshot.created_at)
        .all()
    )

    previous_hash = "GENESIS"

    for s in snapshots:
        payload = (
            f"{s.tenant_id}"
            f"{s.risk_level}"
            f"{s.context}"
            f"{s.strategy_stats_json}"
            f"{s.selected_strategy}"
            f"{s.regret}"
            f"{s.random_seed}"
            f"{previous_hash}"
        )

        recalculated_hash = compute_hash(payload)

        if recalculated_hash != s.current_hash:
            return False

        previous_hash = s.current_hash

    return True