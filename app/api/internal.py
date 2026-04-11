from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings
from app.core.metrics import latency_tracker

router = APIRouter(prefix="/internal", tags=["internal"])

def verify_internal_access():
    if settings.ENV != "development":
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/metrics", dependencies=[Depends(verify_internal_access)])
def get_metrics():
    return {
        "latency": latency_tracker.percentiles()
    }