import hashlib
import json


def hash_payload(payload: dict) -> str:
    if not payload:
        return ""
    encoded = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def fingerprint_request(ip: str, endpoint: str) -> str:
    raw = f"{ip}:{endpoint}"
    return hashlib.md5(raw.encode()).hexdigest()
