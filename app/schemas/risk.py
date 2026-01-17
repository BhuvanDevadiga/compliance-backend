from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List


class RiskScoreRequest(BaseModel):
    company_size: int = Field(..., gt=0, le=10000)
    industry: str = Field(..., min_length=2)
    has_gst: bool
    has_pan: bool


class RiskScoreResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: List[str]


class RiskScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_size: int
    industry: str
    has_gst: bool
    has_pan: bool
    risk_score: int
    risk_level: str
    created_at: datetime
  


