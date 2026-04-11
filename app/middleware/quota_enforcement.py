from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import date

from app.services.quota_service import get_quota_snapshot
from app.services.tenant_usage_service import get_today_usage
from app.db.database import SessionLocal

SKIP_PATH_PREFIXES = (
    "/docs",
    "/openapi.json",
    "/health",
)

class QuotaEnforcementMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip non-business endpoints
        if path.startswith(SKIP_PATH_PREFIXES):
            return await call_next(request)

        tenant = getattr(request.state, "tenant", None)
        if not tenant:
            return await call_next(request)

        db = SessionLocal()
        try:
            quota = get_quota_snapshot(db, tenant.tenant_id)
            if not quota:
                return await call_next(request)

            usage_today = get_today_usage(db, tenant.tenant_id)

            if (
                quota["daily_limit"] is not None
                and quota["daily_limit"] > 0
                and usage_today >= quota["daily_limit"]
            ):
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "DAILY_QUOTA_EXCEEDED",
                        "daily_limit": quota["daily_limit"],
                        "used_today": usage_today,
                    },
                )

            return await call_next(request)

        finally:
            db.close()
