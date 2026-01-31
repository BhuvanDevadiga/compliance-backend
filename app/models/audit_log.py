from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.base import Base


class RequestAuditLog(Base):
    __tablename__ = "request_audit_logs"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False)
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)

    response_time_ms = Column(Integer, nullable=False)
    correlation_id = Column(String(36), nullable=False)
    request_id = Column(Text)
    api_key_hash = Column(Text)
    latency_ms = Column(Integer)
    ip_address = Column(Text)
    user_agent = Column(Text)
    request_hash = Column(Text)
    response_size = Column(Integer)

    created_at = Column(DateTime, server_default=func.now())