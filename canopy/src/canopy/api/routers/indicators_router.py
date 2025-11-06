"""
Indicators Router - Endpoints for technical indicators.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field

router = APIRouter()


class IndicatorInfo(BaseModel):
    """Information about a technical indicator."""

    name: str
    description: str
    parameters: List[Dict[str, Any]]
    example: str
    category: str


@router.get("/list")
async def list_indicators() -> Dict[str, Any]:
    """
    List all available technical indicators.

    Returns:
        List of indicators with their descriptions
    """
    indicators = [
        {
            "name": "sma",
            "description": "Simple Moving Average",
            "parameters": [
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "period", "type": "int", "description": "Period length"},
            ],
            "example": "sma(close, 20)",
            "category": "trend",
        },
        {
            "name": "ema",
            "description": "Exponential Moving Average",
            "parameters": [
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "period", "type": "int", "description": "Period length"},
            ],
            "example": "ema(close, 12)",
            "category": "trend",
        },
        {
            "name": "rsi",
            "description": "Relative Strength Index",
            "parameters": [
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "period", "type": "int", "description": "Period length (default: 14)"},
            ],
            "example": "rsi(close, 14)",
            "category": "momentum",
        },
        {
            "name": "macd",
            "description": "Moving Average Convergence Divergence",
            "parameters": [
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "fast", "type": "int", "description": "Fast period (default: 12)"},
                {"name": "slow", "type": "int", "description": "Slow period (default: 26)"},
                {"name": "signal", "type": "int", "description": "Signal period (default: 9)"},
            ],
            "example": "macd(close, 12, 26, 9)",
            "category": "momentum",
        },
        {
            "name": "bollinger_bands",
            "description": "Bollinger Bands",
            "parameters": [
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "period", "type": "int", "description": "Period length (default: 20)"},
                {"name": "std_dev", "type": "float", "description": "Standard deviations (default: 2.0)"},
            ],
            "example": "bollinger_bands(close, 20, 2.0)",
            "category": "volatility",
        },
        {
            "name": "atr",
            "description": "Average True Range",
            "parameters": [
                {"name": "period", "type": "int", "description": "Period length (default: 14)"},
            ],
            "example": "atr(14)",
            "category": "volatility",
        },
        {
            "name": "stochastic",
            "description": "Stochastic Oscillator",
            "parameters": [
                {"name": "k_period", "type": "int", "description": "K period (default: 14)"},
                {"name": "d_period", "type": "int", "description": "D period (default: 3)"},
            ],
            "example": "stochastic(14, 3)",
            "category": "momentum",
        },
        {
            "name": "adx",
            "description": "Average Directional Index",
            "parameters": [
                {"name": "period", "type": "int", "description": "Period length (default: 14)"},
            ],
            "example": "adx(14)",
            "category": "trend",
        },
    ]

    # Group by category
    categories = {}
    for ind in indicators:
        cat = ind["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ind)

    return {
        "indicators": indicators,
        "categories": categories,
        "total_count": len(indicators),
    }


@router.get("/{indicator_name}")
async def get_indicator_info(indicator_name: str) -> IndicatorInfo:
    """
    Get detailed information about a specific indicator.

    Args:
        indicator_name: Name of the indicator

    Returns:
        Indicator details
    """
    # This would be replaced with actual indicator registry
    indicators_map = {
        "sma": IndicatorInfo(
            name="sma",
            description="Simple Moving Average - The average price over a specified period",
            parameters=[
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "period", "type": "int", "description": "Period length"},
            ],
            example="fast_ma = sma(close, 50)\nslow_ma = sma(close, 200)",
            category="trend",
        ),
        "rsi": IndicatorInfo(
            name="rsi",
            description="Relative Strength Index - Momentum oscillator measuring speed and magnitude of price changes",
            parameters=[
                {"name": "data", "type": "series", "description": "Input data series"},
                {"name": "period", "type": "int", "description": "Period length (default: 14)"},
            ],
            example="rsi_14 = rsi(close, 14)\nbuy when rsi_14 < 30\nsell when rsi_14 > 70",
            category="momentum",
        ),
    }

    if indicator_name not in indicators_map:
        raise HTTPException(status_code=404, detail=f"Indicator '{indicator_name}' not found")

    return indicators_map[indicator_name]


@router.get("/categories/list")
async def list_categories() -> Dict[str, Any]:
    """
    List indicator categories.

    Returns:
        List of indicator categories
    """
    categories = [
        {
            "name": "trend",
            "description": "Trend-following indicators",
            "examples": ["SMA", "EMA", "ADX"],
        },
        {
            "name": "momentum",
            "description": "Momentum and oscillator indicators",
            "examples": ["RSI", "MACD", "Stochastic"],
        },
        {
            "name": "volatility",
            "description": "Volatility indicators",
            "examples": ["Bollinger Bands", "ATR"],
        },
        {
            "name": "volume",
            "description": "Volume-based indicators",
            "examples": ["OBV", "VWAP"],
        },
    ]

    return {
        "categories": categories,
        "count": len(categories),
    }
