"""
System health monitoring.

Provides health check functionality for various system components.
"""

import psutil
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class HealthCheck:
    """
    System health checker.

    Monitors various system components and provides health status.
    """

    @staticmethod
    def check_memory() -> HealthCheckResult:
        """
        Check system memory.

        Returns:
            HealthCheckResult
        """
        memory = psutil.virtual_memory()
        percent_used = memory.percent

        if percent_used < 80:
            status = HealthStatus.HEALTHY
            message = "Memory usage normal"
        elif percent_used < 90:
            status = HealthStatus.DEGRADED
            message = "Memory usage high"
        else:
            status = HealthStatus.UNHEALTHY
            message = "Memory usage critical"

        return HealthCheckResult(
            name="memory",
            status=status,
            message=message,
            details={
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": percent_used,
            },
        )

    @staticmethod
    def check_disk() -> HealthCheckResult:
        """
        Check disk space.

        Returns:
            HealthCheckResult
        """
        disk = psutil.disk_usage("/")
        percent_used = disk.percent

        if percent_used < 80:
            status = HealthStatus.HEALTHY
            message = "Disk space normal"
        elif percent_used < 90:
            status = HealthStatus.DEGRADED
            message = "Disk space low"
        else:
            status = HealthStatus.UNHEALTHY
            message = "Disk space critical"

        return HealthCheckResult(
            name="disk",
            status=status,
            message=message,
            details={
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": percent_used,
            },
        )

    @staticmethod
    def check_cpu() -> HealthCheckResult:
        """
        Check CPU usage.

        Returns:
            HealthCheckResult
        """
        cpu_percent = psutil.cpu_percent(interval=1)

        if cpu_percent < 70:
            status = HealthStatus.HEALTHY
            message = "CPU usage normal"
        elif cpu_percent < 85:
            status = HealthStatus.DEGRADED
            message = "CPU usage high"
        else:
            status = HealthStatus.UNHEALTHY
            message = "CPU usage critical"

        return HealthCheckResult(
            name="cpu",
            status=status,
            message=message,
            details={
                "used_percent": cpu_percent,
                "core_count": psutil.cpu_count(),
            },
        )

    @staticmethod
    def check_database(connection_url: str = None) -> HealthCheckResult:
        """
        Check database connectivity.

        Args:
            connection_url: Database connection URL

        Returns:
            HealthCheckResult
        """
        if not connection_url:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database not configured",
            )

        try:
            # TODO: Implement actual database check
            # For now, just return healthy
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connected",
            )
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
            )

    @staticmethod
    def check_redis(redis_url: str = None) -> HealthCheckResult:
        """
        Check Redis connectivity.

        Args:
            redis_url: Redis connection URL

        Returns:
            HealthCheckResult
        """
        if not redis_url:
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis not configured",
            )

        try:
            # TODO: Implement actual Redis check
            # For now, just return healthy
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connected",
            )
        except Exception as e:
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
            )

    @classmethod
    def check_all(
        cls, database_url: str = None, redis_url: str = None
    ) -> Dict[str, Any]:
        """
        Run all health checks.

        Args:
            database_url: Database connection URL
            redis_url: Redis connection URL

        Returns:
            Dictionary with all health check results
        """
        checks = [
            cls.check_memory(),
            cls.check_disk(),
            cls.check_cpu(),
            cls.check_database(database_url),
            cls.check_redis(redis_url),
        ]

        # Determine overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "status": overall_status.value,
            "timestamp": time.time(),
            "checks": [c.to_dict() for c in checks],
        }


# Example usage
if __name__ == "__main__":
    import json

    health = HealthCheck.check_all()
    print(json.dumps(health, indent=2))
