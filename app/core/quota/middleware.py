from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import date

from app.db.database import SessionLocal
from app.models.tenant_quota import TenantQuota
from app.models.tenant_usage import TenantUsage


class TenantQuotaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        tenant_id = request.headers.get("X-Tenant-ID")

       
        if not tenant_id:
            return await call_next(request)

        db = SessionLocal()
        try:
            quota = (
                db.query(TenantQuota)
                .filter(TenantQuota.tenant_id == tenant_id)
                .first()
            )

            
            if not quota:
                return await call_next(request)

            today = date.today()

            usage = (
                db.query(TenantUsage)
                .filter(
                    TenantUsage.tenant_id == tenant_id,
                    TenantUsage.usage_date == today,
                )
                .with_entities(TenantUsage.request_count)
                .all()
            )

            used_today = sum(row[0] for row in usage)

            if quota.enforce_hard_limit and used_today >= quota.daily_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Daily API quota exceeded",
                        "limit": quota.daily_limit,
                        "used": used_today,
                        "plan": quota.plan,
                    },
                )

        finally:
            db.close()

        return await call_next(request)
