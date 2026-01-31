from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog


def write_audit_log(payload: dict) -> None:
    db: Session = SessionLocal()
    try:
        db.add(AuditLog(**payload))
        db.commit()
    except Exception as e:
        db.rollback()
        # DO NOT raise — audit must be non-fatal
        print("[AUDIT][ERROR]", str(e))
    finally:
        db.close()
