import threading
from collections import deque
import numpy as np

class LatencyTracker:
    def __init__(self, max_samples=10000):
        self.samples = deque(maxlen=max_samples)
        self.lock = threading.Lock()

    def record(self, value):
        with self.lock:
            self.samples.append(value)

    def percentile(self):
        with self.lock:
            if not self.samples:
                return None
            arr = np.array(self.samples)
            return {
                "p50": np.percentile(arr, 50),
                "p95": np.percentile(arr, 95),
                "p99": np.percentile(arr, 99),
            }
latency_tracker = LatencyTracker()        