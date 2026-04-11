from contextlib import asynccontextmanager, suppress
import asyncio
import logging
import os
import threading

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import TimeoutError
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

import app.models  # noqa: F401
from app.api import risk_metadata
from app.api.admin.admin_intelligence_router import router as admin_intelligence_router
from app.api.admin.anomaly import router as anomaly_router
from app.api.admin.insight import router as insight_router
from app.api.admin.intelligence import router as intelligence_router
from app.api.admin.live_events import router as live_events_router
from app.api.admin.live_risk import router as live_risk_router
from app.api.admin.mitigate import router as mitigate_router
from app.api.admin.mitigation_history import router as mitigation_history_router
from app.api.admin.mitigation_insights import router as mitigation_router
from app.api.admin.policy_insight import router as policy_router
from app.api.admin.predict import router as predict_router
from app.api.admin.trend import router as trend_router
from app.api.admin_events import router as admin_events_router
from app.api.admin_overview import router as overview_router
from app.api.admin_risk import router as admin_risk_router
from app.api.admin_simulation import router as simulation_router
from app.api.admin_timeline import router as admin_timeline_router
from app.api.analytics import router as analytics_router
from app.api.autonomous import router as autonomous_router
from app.api.autonomous_loop import router as loop_router
from app.api.autonomous_policy import router as autonomous_policy_router
from app.api.debug import router as debug_router
from app.api.dashboard import api_router as dashboard_api_router
from app.api.dashboard import router as dashboard_router
from app.api.explain import router as explain_router
from app.api.feedback import router as feedback_router
from app.api.governance import metrics_router as governance_metrics_router
from app.api.governance import router as governance_router
from app.api.governance_alerts import governance_alerts
from app.api.health import router as health_router
from app.api.internal import router as internal_router
from app.api.internal.audit import router as internal_audit_router
from app.api.internal.timeline import router as internal_timeline_router
from app.api.internal.tenant_usage import router as tenant_usage_router
from app.api.internal.usage import router as internal_usage_router
from app.api.internal.usage_analytics import router as usage_analytics_router
from app.api.ml import router as ml_router
from app.api.ml_governance import router as ml_governance_router
from app.api.ml_predict import router as ml_predict_router
from app.api.public.risk import router as public_risk_router
from app.api.risk import router as risk_router
from app.api.risk_metadata import router as risk_metadata_router
from app.api.system import router as system_router
from app.api.tenant import router as tenant_router
from app.background.predictive_worker import start_predictive_worker
from app.background.profiler_worker import profiler_loop, start_profiler_worker
from app.background.risk_decay_worker import risk_decay_loop
from app.background.stabilization_worker import start_stabilization_worker
from app.core.abuse.middleware import AbuseProtectionMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.metrics import latency_tracker
from app.core.quota.middleware import TenantQuotaMiddleware
from app.core.rate_limiter import limiter
from app.core.redis_client import redis_client
from app.db.database import engine
from app.middleware.error_handler import global_exception_handler
from app.middleware.quota_enforcement import QuotaEnforcementMiddleware
from app.middleware.request_logging import request_logging_middleware
from app.middleware.security_headers import security_headers_middleware
from app.models.usage_counter import UsageCounter
from app.observability.audit_middleware import AuditMiddleware
from app.services.anchor_scheduler import anchor_loop
from app.services.autonomous_scheduler import scheduler, start_autonomous_scheduler
from app.middleware.adaptive_rate_limiter import adaptive_rate_limiter
from app.services.risk_refresh_scheduler import start_scheduler 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from app.api.auth import router as auth_router

def _env_truthy(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


setup_logging()
logger = logging.getLogger("app.lifecycle")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup")
    start_scheduler()

    if _env_truthy("ENABLE_BACKGROUND_WORKERS", "true"):
        start_profiler_worker()
        logger.info("profiler_worker_running")
    else:
        logger.info("background_workers_disabled")

    if _env_truthy("ENABLE_PROFILER_THREAD", "false"):
        threading.Thread(target=profiler_loop, daemon=True).start()
        logger.info("profiler_thread_started")

    app.state.anchor_task = None

    if _env_truthy("ENABLE_BACKGROUND_WORKERS", "true"):
        threading.Thread(target=risk_decay_loop, daemon=True).start()
        start_stabilization_worker()
        start_predictive_worker()
        start_autonomous_scheduler()
        app.state.anchor_task = asyncio.create_task(anchor_loop())
        logger.info("background_workers_started")

    try:
        yield
    finally:
        logger.info("application_shutdown")

        anchor_task = getattr(app.state, "anchor_task", None)
        if anchor_task is not None:
            anchor_task.cancel()
            with suppress(asyncio.CancelledError):
                await anchor_task

        if getattr(scheduler, "running", False):
            scheduler.shutdown(wait=False)

        redis_client.close()
        engine.dispose()


app = FastAPI(
    title="Compliance Risk Engine",
    debug=settings.DEBUG,
    lifespan=lifespan,
)
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(adaptive_rate_limiter)
latency_tracker = latency_tracker

app.add_exception_handler(Exception, global_exception_handler)


@app.exception_handler(TimeoutError)
async def db_timeout_handler(request: Request, exc: TimeoutError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database overloaded. Please retry."},
    )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


if _env_truthy("ENABLE_AUDIT_MIDDLEWARE", "true"):
    app.add_middleware(AuditMiddleware)
app.add_middleware(AbuseProtectionMiddleware)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(SlowAPIMiddleware)
# app.add_middleware(AuditLogMiddleware)  <-- comment out Phase-2.1 middleware temporarily


if settings.RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
if _env_truthy("ENABLE_QUOTA_MIDDLEWARE", "true"):
    app.add_middleware(TenantQuotaMiddleware)

app.include_router(public_risk_router)
app.include_router(risk_metadata_router)
app.include_router(health_router)
app.include_router(tenant_usage_router)
app.include_router(usage_analytics_router)
app.include_router(internal_usage_router)
app.include_router(debug_router)
app.include_router(analytics_router)
app.include_router(internal_audit_router)
app.include_router(internal_timeline_router)
app.include_router(admin_risk_router)
app.include_router(admin_events_router)
app.include_router(simulation_router)
app.include_router(overview_router)
app.include_router(admin_timeline_router)
app.include_router(live_risk_router)
app.include_router(live_events_router)
app.include_router(insight_router)
app.include_router(trend_router)
app.include_router(predict_router)
app.include_router(mitigate_router)
app.include_router(mitigation_history_router)
app.include_router(anomaly_router)
app.include_router(intelligence_router)
app.include_router(mitigation_router)
app.include_router(policy_router)
app.include_router(autonomous_router)
app.include_router(autonomous_policy_router)
app.include_router(loop_router)
app.include_router(admin_intelligence_router)
app.include_router(ml_router)
app.include_router(ml_governance_router)
app.include_router(ml_predict_router)
app.include_router(system_router)
app.include_router(tenant_router)
app.include_router(governance_router)
app.include_router(governance_metrics_router)
app.include_router(explain_router)
app.include_router(feedback_router)
app.include_router(governance_alerts)
app.include_router(internal_router)
app.include_router(dashboard_router)
app.include_router(dashboard_api_router)
app.include_router(auth_router)


if _env_truthy("ENABLE_QUOTA_MIDDLEWARE", "true"):
    app.add_middleware(QuotaEnforcementMiddleware)
if _env_truthy("ENABLE_AUDIT_MIDDLEWARE", "true"):
    app.add_middleware(AuditMiddleware)

@app.get("/")
def serve_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )


@app.get("/dashboard-ui")
def serve_dashboard_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )


@app.get("/login")
def serve_login():
    return FileResponse("templates/login.html")
