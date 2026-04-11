from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auto_mitigation import auto_mitigate

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/mitigate/{tenant_id}")
def mitigate(tenant_id: str, db: Session = Depends(get_db)):
    with db.begin():
        return auto_mitigate(db, tenant_id)
