from sqlalchemy.orm import Session
from app.models.tenant_risk_state import TenantRiskState
import time, logging

logger= logging.getLogger("tenant_lock")

def acquire_tenant_lock(db: Session, tenant_id: str) :
    start = time.monotonic()

    tenant_state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .with_for_update()
        .first()
    )
    lock_time = time.monotonic() - start

    if lock_time>0.05:
        logger.warning(
            f"[LOCK WAIT] tenant={tenant_id} wait={lock_time:.4f}s"
        )

    if tenant_state:
        return tenant_state

    # Genesis-safe creation
    tenant_state = TenantRiskState(
        tenant_id=tenant_id,
        risk_score=0.0,
        risk_level="LOW",
        quarantined=False,
    )

    db.add(tenant_state)
    db.flush()  # force insert to respect unique constraint

    # Re-lock to maintain consistent lock acquisition order
    tenant_state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant_id)
        .with_for_update()
        .one()
    )

    return tenant_state
