from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON, Boolean, UniqueConstraint
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, index=True)
    business_type = Column(String)
    state = Column(String)

class Compliance(Base):
    __tablename__ = "compliances"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    frequency = Column(String)
    due_day = Column(Integer)
    penalty = Column(String)

class UserCompliance(Base):
    __tablename__ = "user_compliances"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    compliance_code = Column(String)
    compliance_type = Column(String)
    due_date = Column(Date)
    status = Column(String, default="PENDING")
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "compliance_code",
            "due_date",
            name="uq_user_compliance"
        ),
    )

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    type = Column(String)
    extracted_data = Column(JSON)
    s3_key = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True)
    gst_registered = Column(Boolean, default=False)
    has_employees_or_contractors = Column(Boolean, default=False)

from sqlalchemy import DateTime
from datetime import datetime

class ComplianceAuditLog(Base):
    __tablename__ = "compliance_audit_logs"

    id = Column(Integer, primary_key=True)
    compliance_id = Column(Integer, ForeignKey("user_compliances.id"))
    old_status = Column(String)
    new_status = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(String)  # "SYSTEM" or user_id
