from fastapi import FastAPI
from app.db.base import Base
from app.db.database import engine
from app.models import risk
from app.api.risk import router as risk_router

app = FastAPI(title="Compliance Risk Engine")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(risk_router, prefix="/api/risk", tags=["Risk"])




