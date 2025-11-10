"""
API Routers - FastAPI route handlers.
"""

from canopy.api.routers.strategies import router as strategies_router
from canopy.api.routers.backtests import router as backtests_router
from canopy.api.routers.data import router as data_router
from canopy.api.routers.indicators import router as indicators_router

__all__ = [
    "strategies_router",
    "backtests_router",
    "data_router",
    "indicators_router",
]
