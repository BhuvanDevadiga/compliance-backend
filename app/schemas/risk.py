from pydantic import BaseModel
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


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
    id: int
    company_size: int
    industry: str
    has_gst: bool
    has_pan: bool
    risk_score: int
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True   


