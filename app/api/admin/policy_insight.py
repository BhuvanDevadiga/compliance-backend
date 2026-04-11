from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.tenant_policy import TenantPolicy
from app.services.policy_runtime import refresh_policy_for_tenant

router = APIRouter(prefix="/admin/policy", tags=["Policy Insight"])


@router.get("/{tenant_id}")
def get_policy_insight(tenant_id: str):
    db: Session = SessionLocal()

    try:
        record = db.query(TenantPolicy).filter_by(
            tenant_id=tenant_id
        ).first()

        if record:
            return {
                "tenant_id": tenant_id,
                "policy": record.policy_name,
                "reason": record.reason_snapshot,
                "last_updated": record.updated_at,
            }

        # Compute and persist policy snapshot on demand when tenant has no policy row yet.
        policy, snapshot = refresh_policy_for_tenant(tenant_id)
        return {
            "tenant_id": tenant_id,
            "policy": policy.name,
            "reason": {
                "source": "computed_snapshot",
                "risk_index": snapshot.risk_index,
                "repeat_score": snapshot.repeat_offense_score,
            },
            "last_updated": snapshot.timestamp,
        }

    finally:
        db.close()
