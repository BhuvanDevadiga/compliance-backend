from fastapi import FastAPI
from app.db.base import Base
from app.db.database import engine
from app.core.logging import setup_logging
from app.api.risk import router as risk_router
from app.api.health import router as health_router

setup_logging()

app = FastAPI(title="Compliance Risk Engine")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(risk_router, prefix="/api/risk")
app.include_router(health_router)
