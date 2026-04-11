from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import get_current_tenant
from app.services.timeline_service import get_tenant_timeline

router = APIRouter(
    prefix="/api/internal",
    tags=["Internal Timeline"],
)


@router.get("/timeline")
def tenant_timeline(
    limit: int = 50,
    db: Session = Depends(get_db),
    tenant=Depends(get_current_tenant),
):
    return get_tenant_timeline(db, tenant.tenant_id, limit)
