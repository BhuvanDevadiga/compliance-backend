from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.predictive_risk import predict_risk

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/predict/{tenant_id}")
def tenant_prediction(tenant_id: str, db: Session = Depends(get_db)):
    return predict_risk(db, tenant_id)
