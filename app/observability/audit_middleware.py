from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.models.tenant import Tenant
from app.models.tenant_api_key import TenantAPIKey
from app.observability.request_id import get_or_create_request_id
from app.observability.hashing import hash_payload
from app.services.observability_service import write_audit_log
from app.services.tenant_usage_monthly_service import increment_monthly_usage
from app.services.tenant_usage_service import increment_daily_usage, increment_tenant_usage
from app.services.quota_service import get_quota_snapshot
from app.services.quota_alert_service import maybe_fire_quota_alert
from app.db.database import SessionLocal
from sqlalchemy.orm import object_session
from sqlalchemy import inspect
from sqlalchemy.orm.exc import DetachedInstanceError
from app.services.usage_counter_service import increment_usage
from app.services.anomaly_detector import detect_anomalies
from app.core.security import hash_api_key



import time

IGNORED_PATH_PREFIXES = (
    "/docs",
    "/openapi.json",
    "/redoc",
)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = get_or_create_request_id(request)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        # Skip infra & docs endpoints
        if request.url.path.startswith(IGNORED_PATH_PREFIXES):
            return response

        db = SessionLocal()
        try:
            # Tenant must come from auth dependency (fallback to API key)
            tenant = getattr(request.state, "tenant", None)
            api_key = request.headers.get("X-API-Key")
            if tenant is None and api_key:
                key_hash = hash_api_key(api_key)
                key_record = (
                    db.query(TenantAPIKey)
                    .filter(
                        TenantAPIKey.key_hash == key_hash,
                        TenantAPIKey.is_active == True,
                    )
                    .first()
                )
                if key_record:
                    tenant = (
                        db.query(Tenant)
                        .filter(Tenant.tenant_id == key_record.tenant_id)
                        .first()
                    )
                if tenant:
                    request.state.tenant = tenant
                    request.state.api_key = api_key

            # Re-attach detached tenant if needed (auth dependency session closed)
            tenant_id_value = None
            if tenant is not None:
                try:
                    tenant_id_value = tenant.tenant_id
                except DetachedInstanceError:
                    try:
                        identity = inspect(tenant).identity
                        if identity:
                            tenant_id_value = identity[0]
                    except Exception:
                        tenant_id_value = None
            if tenant is not None and object_session(tenant) is None:
                tenant = None
                if tenant_id_value is not None:
                    if isinstance(tenant_id_value, int):
                        tenant = db.query(Tenant).filter(Tenant.id == tenant_id_value).first()
                    else:
                        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id_value).first()
            if tenant is None:
                return response

            # Ruleset version from risk engine (for forensic tracing)
            ruleset_version = getattr(request.state, "ruleset_version", None)

            latency_ms = int((time.time() - start_time) * 1000)
            api_key = getattr(request.state, "api_key", None)

            audit_payload = {
                "request_id": request_id,
                "tenant_id": tenant.tenant_id,
                "api_key_hash": hash_payload(api_key) if api_key else None,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("User-Agent"),
                "request_hash": hash_payload(f"{request.method}:{request.url.path}"),
                "response_size": (
                    int(response.headers.get("content-length"))
                    if response.headers.get("content-length")
                    else None
                ),
                "ruleset_version": ruleset_version,
            }
            if tenant:
                increment_usage(tenant.tenant_id)

            write_audit_log(db, audit_payload)

            # Only increment usage if request did NOT exceed quota
            if response.status_code != 429:
                increment_tenant_usage(
                    db=db,
                    tenant_id=tenant.tenant_id,
                    path=request.url.path,
                    method=request.method,
                )
                increment_daily_usage(
                    db=db,
                    tenant_id=tenant.tenant_id,
                    path=request.url.path,
                    method=request.method,
                )
                increment_monthly_usage(
                    db=db,
                    tenant_id=tenant.tenant_id,
                    path=request.url.path,
                    method=request.method,
                )

                quota = get_quota_snapshot(db, tenant.tenant_id)
                if quota.get("daily_limit") is not None:
                    maybe_fire_quota_alert(
                        tenant_id=tenant.tenant_id,
                        plan=quota["plan"],
                        daily_limit=quota["daily_limit"],
                        used_today=quota["used"],
                    )

                    detect_anomalies(db, tenant.tenant_id)


        except Exception as e:
            print(f"Audit / usage failed: {e}")
        finally:
            db.close()

        return response
