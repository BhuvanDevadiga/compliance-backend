import time
from collections import defaultdict, deque

# fingerprint -> timestamps
_HITS = defaultdict(deque)

WINDOW_SECONDS = 10
MAX_HITS = 10


def record_hit(fingerprint: str) -> bool:
   
    now = time.time()
    q = _HITS[fingerprint]

    
    while q and q[0] < now - WINDOW_SECONDS:
        q.popleft()

    q.append(now)

    return len(q) > MAX_HITS
