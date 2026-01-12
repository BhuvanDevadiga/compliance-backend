from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.model import Compliance  

router = APIRouter(prefix="/compliance")

@router.get("/")
def list_compliances(db: Session = Depends(get_db)):
    return db.query(Compliance).all()

