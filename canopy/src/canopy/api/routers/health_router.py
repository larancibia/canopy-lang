"""
Health Check Router - System health and status endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


@router.get("")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns system health status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "canopy-api",
    }


@router.get("/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint.

    Returns whether the service is ready to accept requests.
    """
    # TODO: Add checks for database, redis, etc.
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "not_configured",
            "redis": "not_configured",
            "data_providers": "ok",
        },
    }


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint.

    Returns whether the service is alive.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
    }
