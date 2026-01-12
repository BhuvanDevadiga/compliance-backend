from pydantic import BaseModel
from datetime import datetime


class RiskScoreRequest(BaseModel):
    company_size: int
    industry: str
    has_gst: bool
    has_pan: bool


class RiskScoreResponse(BaseModel):
    risk_score: int
    risk_level: str


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
        orm_mode = True


