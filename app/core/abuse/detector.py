# core/abuse/detector.py
from .state import recent_requests

CAPTCHA_THRESHOLD = 100
BLOCK_THRESHOLD = 200

def detect_abuse(ip: str):
    count = len(recent_requests(ip))

    if count >= BLOCK_THRESHOLD:
        return "block"
    if count >= CAPTCHA_THRESHOLD:
        return "captcha"
    return "allow"
