from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)

    company_size = Column(Integer, nullable=False)
    industry = Column(String, nullable=False)
    has_gst = Column(Boolean, nullable=False)
    has_pan = Column(Boolean, nullable=False)

    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=False)
    reasons = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

print(RiskAssessment.__table__.columns.keys()) 

