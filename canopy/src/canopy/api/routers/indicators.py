"""
Indicator Router - Endpoints for technical indicator operations.
"""

from fastapi import APIRouter, HTTPException, status
import pandas as pd
from canopy.api.models.requests import IndicatorCalculateRequest
from canopy.api.models.responses import IndicatorInfoResponse, IndicatorListResponse
from canopy.domain.indicator import SMA, EMA, RSI
from canopy.domain.timeseries import TimeSeries

router = APIRouter(prefix="/indicators", tags=["indicators"])

# Registry of available indicators
INDICATORS = {
    "sma": {
        "class": SMA,
        "name": "SMA",
        "description": "Simple Moving Average - Average of closing prices over N periods",
        "parameters": {"period": "int (required, > 0) - Number of periods for the moving average"},
        "example": "fast_ma = sma(close, 50)",
    },
    "ema": {
        "class": EMA,
        "name": "EMA",
        "description": "Exponential Moving Average - Weighted moving average giving more weight to recent prices",
        "parameters": {"period": "int (required, > 0) - Number of periods for the moving average"},
        "example": "fast_ema = ema(close, 20)",
    },
    "rsi": {
        "class": RSI,
        "name": "RSI",
        "description": "Relative Strength Index - Momentum oscillator measuring speed and magnitude of price changes",
        "parameters": {"period": "int (optional, default 14) - Number of periods for RSI calculation"},
        "example": "rsi_14 = rsi(close, 14)",
    },
}


@router.get("", response_model=IndicatorListResponse)
async def list_indicators():
    """
    List all available technical indicators.

    Returns a list of all indicators that can be used in Canopy strategies.

    Example:
        ```
        GET /api/indicators
        ```
    """
    indicator_names = [info["name"] for info in INDICATORS.values()]
    return IndicatorListResponse(indicators=indicator_names, count=len(indicator_names))


@router.get("/{name}", response_model=IndicatorInfoResponse)
async def get_indicator_info(name: str):
    """
    Get detailed information about a specific indicator.

    Returns documentation, parameters, and usage examples for the indicator.

    Args:
        name: Indicator name (e.g., "sma", "ema", "rsi")

    Example:
        ```
        GET /api/indicators/sma
        ```
    """
    name = name.lower()

    if name not in INDICATORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{name}' not found",
        )

    info = INDICATORS[name]
    return IndicatorInfoResponse(
        name=info["name"],
        description=info["description"],
        parameters=info["parameters"],
        example=info["example"],
    )


@router.post("/{name}/calculate")
async def calculate_indicator(name: str, request: IndicatorCalculateRequest):
    """
    Calculate an indicator on provided data.

    Calculates the specified indicator using the provided price data
    and parameters.

    Args:
        name: Indicator name (e.g., "sma", "ema", "rsi")
        request: Request containing data and parameters

    Example:
        ```
        POST /api/indicators/sma/calculate
        {
            "data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111],
            "params": {"period": 5}
        }
        ```

    Returns:
        Calculated indicator values
    """
    name = name.lower()

    if name not in INDICATORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{name}' not found",
        )

    try:
        # Create indicator instance
        indicator_class = INDICATORS[name]["class"]
        params = request.params or {}

        # Validate required parameters
        if name in ["sma", "ema"] and "period" not in params:
            raise ValueError("Parameter 'period' is required")

        indicator = indicator_class(**params)

        # Create dummy timeseries from data
        close_series = pd.Series(request.data, index=pd.date_range("2020-01-01", periods=len(request.data)))
        timeseries = TimeSeries(
            open=close_series,
            high=close_series,
            low=close_series,
            close=close_series,
            volume=pd.Series([0] * len(request.data), index=close_series.index),
        )

        # Calculate indicator
        result = indicator.calculate(timeseries)

        # Convert to list (handle NaN values)
        result_list = [None if pd.isna(val) else float(val) for val in result]

        return {
            "indicator": INDICATORS[name]["name"],
            "values": result_list,
            "count": len(result_list),
            "parameters": params,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate indicator: {str(e)}",
        )
