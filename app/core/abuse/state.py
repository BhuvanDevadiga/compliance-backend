# core/abuse/state.py
from collections import defaultdict
from time import time

IP_STATE = defaultdict(list)

def record_request(ip: str):
    IP_STATE[ip].append(time())

def recent_requests(ip: str, window: int = 60):
    now = time()

    # prune old entries
    IP_STATE[ip] = [t for t in IP_STATE[ip] if now - t < window]

    return IP_STATE[ip]
