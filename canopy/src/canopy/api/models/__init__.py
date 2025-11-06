"""
API Models - Pydantic models for request/response validation.
"""

from canopy.api.models.requests import (
    BacktestRequest,
    StrategyParseRequest,
    StrategyValidateRequest,
    IndicatorCalculateRequest,
)
from canopy.api.models.responses import (
    BacktestJobResponse,
    BacktestResultResponse,
    StrategyParseResponse,
    StrategyExampleResponse,
    IndicatorInfoResponse,
    IndicatorListResponse,
    DataProviderResponse,
    ErrorResponse,
)
from canopy.api.models.schemas import (
    JobStatus,
    PerformanceMetricsSchema,
    TradeSchema,
    SignalSchema,
)

__all__ = [
    # Requests
    "BacktestRequest",
    "StrategyParseRequest",
    "StrategyValidateRequest",
    "IndicatorCalculateRequest",
    # Responses
    "BacktestJobResponse",
    "BacktestResultResponse",
    "StrategyParseResponse",
    "StrategyExampleResponse",
    "IndicatorInfoResponse",
    "IndicatorListResponse",
    "DataProviderResponse",
    "ErrorResponse",
    # Schemas
    "JobStatus",
    "PerformanceMetricsSchema",
    "TradeSchema",
    "SignalSchema",
]
