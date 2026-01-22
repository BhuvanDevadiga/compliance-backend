from fastapi import FastAPI
from app.db.base import Base
from app.db.database import engine
from app.core.logging import setup_logging
from app.api.risk import router as risk_router
from app.api.health import router as health_router
from app.api import risk_metadata
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.api.public.risk import router as public_risk_router
from app.api.risk_metadata import router as risk_metadata_router
from app.core.abuse.middleware import AbuseProtectionMiddleware

setup_logging()

app = FastAPI(title="Compliance Risk Engine")

app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.include_router(risk_metadata.router)
app.add_middleware(AbuseProtectionMiddleware)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(public_risk_router)
app.include_router(risk_metadata_router)
app.include_router(health_router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
