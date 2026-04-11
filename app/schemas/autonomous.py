from pydantic import BaseModel
from datetime import datetime


class DecisionResponse(BaseModel):
    forecast_peak: float
    forecast_accuracy: float
    escalation_score: float
    proactive_triggered: bool
    mitigation_level: str
    final_probability: float
    created_at: datetime

    class Config:
        from_attributes = True

class SystemStateResponse(BaseModel):
    risk_posture: str
    avg_probability: float
    forecast_reliability: float
    escalation_rate: float
    current_mitigation_bias: str
    system_confidence: str        
    watch_threshold: float
    critical_threshold: float