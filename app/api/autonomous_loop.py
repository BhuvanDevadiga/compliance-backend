from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.autonomous_loop import run_autonomous_feedback_cycle

router = APIRouter(
    prefix="/api/autonomous",
    tags=["Autonomous Loop"],
)
@router.post("/run/{tenant_id}")
def run_cycle(tenant_id: str, db: Session = Depends(get_db)):
    """
    Runs the full autonomous feedback cycle for a tenant.
    """
    result = run_autonomous_feedback_cycle(db, tenant_id)
    return result
