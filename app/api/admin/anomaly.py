from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.anomaly_detection import detect_anomaly

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/anomaly/{tenant_id}")
def anomaly(tenant_id: str, db: Session = Depends(get_db)):
    return detect_anomaly(db, tenant_id)
