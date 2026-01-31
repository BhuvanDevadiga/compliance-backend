from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import get_current_tenant
from app.services.quota_service import get_quota_snapshot

router = APIRouter(prefix="/api/debug", tags=["Debug"])


@router.get("/quota")
def quota_debug(
    tenant=Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return get_quota_snapshot(db, tenant.id)
