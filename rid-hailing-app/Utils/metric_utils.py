import time

class Metrics:
    def __init__(self):
        self.counters = {}
        self.timers = {}

    def inc(self, name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[name] = self.counters.get(name, 0) + value

    def start_timer(self, name: str):
        """Start a timer."""
        self.timers[name] = time.time()

    def stop_timer(self, name: str):
        """Stop a timer and return duration in seconds."""
        if name in self.timers:
            duration = time.time() - self.timers[name]
            del self.timers[name]
            return duration
        return None

    def report(self):
        """Print metrics (could be pushed to monitoring system)."""
        print("=== Metrics Report ===")
        for k, v in self.counters.items():
            print(f"{k}: {v}")

    


### usage in files 

from utils.metrics_utils import Metrics
metrics = Metrics()

# Count processed messages
metrics.inc("processed_messages")

# Measure latency
metrics.start_timer("latency")
# ... do work ...
print("Latency:", metrics.stop_timer("latency"))

metrics.report()
