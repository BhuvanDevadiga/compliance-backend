from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.models import tenant
from app.observability.request_id import get_or_create_request_id
from app.observability.hashing import hash_payload
from app.services.observability_service import write_audit_log
from app.services.tenant_usage_monthly_service import increment_monthly_usage
from app.services.tenant_usage_service import increment_daily_usage, increment_tenant_usage
from app.services.quota_service import get_quota_snapshot
from app.services.quota_alert_service import maybe_fire_quota_alert
from app.db.database import SessionLocal


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

        # 🚫 Skip infra & docs endpoints
        if request.url.path.startswith(IGNORED_PATH_PREFIXES):
            return response

        # 🔑 Tenant must come from auth dependency
        tenant = getattr(request.state, "tenant", None)
        if tenant is None:
            return response

        latency_ms = int((time.time() - start_time) * 1000)
        api_key = getattr(request.state, "api_key", None)

        audit_payload = {
            "request_id": request_id,
            "tenant_id": tenant.id,
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
        }

        db = SessionLocal()
        try:
            write_audit_log(db, audit_payload)

            if response.status_code != 429:
                increment_tenant_usage(
                    db=db,
                    tenant_id=tenant.id,
                    path=request.url.path,
                    method=request.method,
                )
                increment_daily_usage(
                    db=db,
                    tenant_id=tenant.id,
                    path=request.url.path,
                    method=request.method,
                )
                increment_monthly_usage(
                    db=db,
                    tenant_id=tenant.id,
                    path=request.url.path,
                    method=request.method,
                )

                quota = get_quota_snapshot(db, tenant.id)
                if quota.get("daily_limit") is not None:
                    maybe_fire_quota_alert(
                        tenant_id=tenant.id,
                        plan=quota["plan"],
                        daily_limit=quota["daily_limit"],
                        used_today=quota["used"],
                    )

        except Exception as e:
            print(f"⚠️ Audit / usage failed: {e}")
        finally:
            db.close()

        return response