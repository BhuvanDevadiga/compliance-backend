from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.abuse.detector import is_suspicious


class AbuseProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        if request.url.path.startswith("/api/public/"):
            suspicious = is_suspicious(request)

            if suspicious:
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests",
                        "reason": "burst_detected",
                        "action": "slow_down",
                    },
                )

        return await call_next(request)
