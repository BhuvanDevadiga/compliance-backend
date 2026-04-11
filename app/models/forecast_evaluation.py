from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class ForecastEvaluation(Base):
    __tablename__ = "forecast_evaluation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, index=True, nullable=False)
    predicted_peak=Column(Float)
    actual_next = Column(Float)
    error = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
