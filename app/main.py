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
from app.observability.audit_middleware import AuditMiddleware
from app.api.internal.tenant_usage import router as tenant_usage_router
from app.core.quota.middleware import TenantQuotaMiddleware
from app.api.internal.usage import router as usage_router
from app.api.internal.usage import router as internal_usage_router
from app.api.debug import router as debug_router
from app.api.analytics import router as analytics_router
from app.api.internal.usage_analytics import router as usage_router


setup_logging()

app = FastAPI(title="Compliance Risk Engine")

app.add_middleware(AuditMiddleware)
app.add_middleware(AbuseProtectionMiddleware)
app.add_middleware(SlowAPIMiddleware)
# app.add_middleware(AuditLogMiddleware)  <-- comment out Phase-2.1 middleware temporarily


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(TenantQuotaMiddleware)

app.include_router(public_risk_router) 
app.include_router(risk_metadata_router)
app.include_router(health_router)
app.include_router(tenant_usage_router)
app.include_router(usage_router)
app.include_router(internal_usage_router)
app.include_router(debug_router)
app.include_router(analytics_router)






@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
