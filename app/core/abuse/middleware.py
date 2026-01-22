from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .state import record_request
from .detector import detect_abuse


class AbuseProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"

        record_request(ip)
        decision = detect_abuse(ip)

        if decision == "block":
            return JSONResponse(
                status_code=429,
                content={"detail": "Blocked due to abuse"}
            )

        if decision == "captcha":
            request.state.require_captcha = True

        return await call_next(request)
