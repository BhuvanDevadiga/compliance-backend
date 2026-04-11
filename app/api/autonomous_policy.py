from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.autonomous_policy_engine import autonomous_policy_adjustment

router = APIRouter(
    prefix="/api/autonomous",
    tags=["Autonomous Policy"],
)

@router.post("/adjust/{tenant_id}")
def adjust_policy(tenant_id: str, db: Session = Depends(get_db)):
    """
    Triggers autonomous policy adjustment engine.
    """
    result = autonomous_policy_adjustment(db, tenant_id)
    return result