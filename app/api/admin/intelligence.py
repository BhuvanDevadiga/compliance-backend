from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.risk_intelligence import compute_risk_intelligence

router = APIRouter(
    prefix="/api/admin/intelligence",
    tags=["Admin Intelligence"],
)


@router.get("/{tenant_id}")
def tenant_intelligence(
    tenant_id: str,
    db: Session = Depends(get_db),
):
    return compute_risk_intelligence(db, tenant_id)
