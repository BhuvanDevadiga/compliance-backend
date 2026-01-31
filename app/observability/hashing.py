import hashlib
import json
from typing import Any

def hash_payload(payload: Any) -> str:
    try:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
    except Exception:
        return "unhashable"
