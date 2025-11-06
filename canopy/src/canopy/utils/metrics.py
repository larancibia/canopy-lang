"""
Performance metrics collection.

Collects and tracks application metrics for monitoring and optimization.
"""

import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import statistics


@dataclass
class Metric:
    """Individual metric data point."""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collect and aggregate application metrics.

    Tracks timing, counters, and custom metrics.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """
        Increment a counter metric.

        Args:
            name: Counter name
            value: Amount to increment
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        self._counters[key] += value

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Set a gauge metric.

        Args:
            name: Gauge name
            value: Gauge value
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        self._gauges[key] = value

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Record a histogram value.

        Args:
            name: Histogram name
            value: Value to record
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        self._histograms[key].append(value)

    def record_timer(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """
        Record a timing metric.

        Args:
            name: Timer name
            duration_ms: Duration in milliseconds
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        self._timers[key].append(duration_ms)

    def get_counter(self, name: str, tags: Dict[str, str] = None) -> int:
        """Get counter value."""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)

    def get_gauge(self, name: str, tags: Dict[str, str] = None) -> float:
        """Get gauge value."""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0.0)

    def get_histogram_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """
        Get histogram statistics.

        Returns:
            Dictionary with count, min, max, mean, median, p95, p99
        """
        key = self._make_key(name, tags)
        values = self._histograms.get(key, [])

        if not values:
            return {}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "min": min(sorted_values),
            "max": max(sorted_values),
            "mean": statistics.mean(sorted_values),
            "median": statistics.median(sorted_values),
            "p95": sorted_values[int(count * 0.95)] if count > 0 else 0,
            "p99": sorted_values[int(count * 0.99)] if count > 0 else 0,
        }

    def get_timer_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """Get timer statistics (same as histogram)."""
        key = self._make_key(name, tags)
        values = self._timers.get(key, [])

        if not values:
            return {}

        return self.get_histogram_stats(name, tags)

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.

        Returns:
            Dictionary with all metrics
        """
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: self.get_histogram_stats(k) for k in self._histograms},
            "timers": {k: self.get_timer_stats(k) for k in self._timers},
        }

    def reset(self):
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()

    @staticmethod
    def _make_key(name: str, tags: Dict[str, str] = None) -> str:
        """Create unique key from name and tags."""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"


class Timer:
    """
    Context manager for timing operations.

    Usage:
        with Timer() as t:
            # do something
        print(f"Took {t.duration_ms}ms")
    """

    def __init__(self, metrics: MetricsCollector = None, name: str = None):
        """
        Initialize timer.

        Args:
            metrics: Optional metrics collector
            name: Optional metric name
        """
        self.metrics = metrics
        self.name = name
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.duration_ms: float | None = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and record metric."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

        if self.metrics and self.name:
            self.metrics.record_timer(self.name, self.duration_ms)


# Global metrics collector instance
_global_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _global_metrics


# Example usage
if __name__ == "__main__":
    collector = MetricsCollector()

    # Counter
    collector.increment_counter("requests_total", tags={"endpoint": "/api/backtests"})
    collector.increment_counter("requests_total", tags={"endpoint": "/api/backtests"})
    print(f"Total requests: {collector.get_counter('requests_total', {'endpoint': '/api/backtests'})}")

    # Gauge
    collector.set_gauge("active_backtests", 5)
    print(f"Active backtests: {collector.get_gauge('active_backtests')}")

    # Histogram
    for i in range(100):
        collector.record_histogram("response_size_bytes", i * 100)

    print("Response size stats:", collector.get_histogram_stats("response_size_bytes"))

    # Timer
    with Timer(collector, "api_request_duration") as t:
        time.sleep(0.1)
    print(f"Request took {t.duration_ms:.2f}ms")
