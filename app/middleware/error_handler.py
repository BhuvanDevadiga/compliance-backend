import logging
from fastapi.responses import JSONResponse
from fastapi import Request

logger = logging.getLogger("app.error")


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )