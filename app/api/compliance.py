from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.compliance_status import update_compliance_status

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.post("/{compliance_id}/status")
def change_status(
    compliance_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    updated = update_compliance_status(
        db=db,
        compliance_id=compliance_id,
        new_status=new_status,
        changed_by="USER"
    )
    return {"message": "Status updated", "status": updated.status}
