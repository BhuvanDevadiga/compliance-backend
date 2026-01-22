from fastapi import Request
from slowapi.util import get_remote_address
from app.core.abuse.state import record_hit
import hashlib


def build_fingerprint(request: Request) -> str:
    ip = get_remote_address(request)
    ua = request.headers.get("user-agent", "unknown")
    path = request.url.path

    raw = f"{ip}:{ua}:{path}"
    return hashlib.sha256(raw.encode()).hexdigest()


def is_suspicious(request: Request) -> bool:
    fingerprint = build_fingerprint(request)
    return record_hit(fingerprint)
