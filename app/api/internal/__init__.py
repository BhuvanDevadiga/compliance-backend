from fastapi import APIRouter

from app.core.metrics import latency_tracker


router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/metrics")
def get_metrics():
    return {
        "latency": latency_tracker.percentiles()
    }
