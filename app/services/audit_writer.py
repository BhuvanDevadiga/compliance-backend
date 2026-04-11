from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.request_audit_log import RequestAuditLog



def write_audit_log(payload: dict) -> None:
    db: Session = SessionLocal()
    try:
        db.add(RequestAuditLog(**payload))
        db.commit()
    except Exception as e:
        db.rollback()
        # DO NOT raise — audit must be non-fatal
        print("[AUDIT][ERROR]", str(e))
    finally:
        db.close()
