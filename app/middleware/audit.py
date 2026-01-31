import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.audit_logger import log_request_audit


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        tenant = getattr(request.state, "tenant", None)

        if tenant:
            try:
                log_request_audit(
                    request=request,
                    response=response,
                    tenant=tenant,
                    start_time=start_time,
                )
            except Exception:
                pass  

        return response
