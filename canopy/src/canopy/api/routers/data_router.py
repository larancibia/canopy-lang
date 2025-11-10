"""
Data Router - Endpoints for fetching market data.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from canopy.adapters.data.provider_factory import DataProviderFactory

router = APIRouter()


class FetchDataRequest(BaseModel):
    """Request model for fetching market data."""

    symbol: str = Field(..., description="Trading symbol (e.g., AAPL)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    provider: str = Field("yahoo", description="Data provider (yahoo, csv)")


class DataPoint(BaseModel):
    """Single data point."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class FetchDataResponse(BaseModel):
    """Response model for market data."""

    symbol: str
    start_date: str
    end_date: str
    data_points: int
    data: List[DataPoint]


@router.post("/fetch", response_model=FetchDataResponse)
async def fetch_market_data(request: FetchDataRequest) -> FetchDataResponse:
    """
    Fetch historical market data.

    Args:
        request: Data fetch parameters

    Returns:
        Historical OHLCV data
    """
    try:
        provider = DataProviderFactory.create(request.provider)
        timeseries = provider.fetch_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        data_points = [
            DataPoint(
                timestamp=bar.timestamp.isoformat(),
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
            )
            for bar in timeseries.bars
        ]

        return FetchDataResponse(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            data_points=len(data_points),
            data=data_points,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/providers")
async def list_data_providers() -> Dict[str, Any]:
    """
    List available data providers.

    Returns:
        List of data providers and their capabilities
    """
    providers = [
        {
            "name": "yahoo",
            "description": "Yahoo Finance (free, no API key required)",
            "supported_assets": ["stocks", "etfs", "indices"],
            "rate_limits": "2000 requests/hour",
            "data_quality": "high",
        },
        {
            "name": "csv",
            "description": "Local CSV files",
            "supported_assets": ["any"],
            "rate_limits": "none",
            "data_quality": "depends on source",
        },
    ]

    return {
        "providers": providers,
        "count": len(providers),
    }


@router.get("/symbols")
async def search_symbols(query: str = "") -> Dict[str, Any]:
    """
    Search for trading symbols.

    Args:
        query: Search query

    Returns:
        List of matching symbols
    """
    # This is a placeholder - implement actual symbol search
    popular_symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ"},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE"},
    ]

    if query:
        filtered = [
            s
            for s in popular_symbols
            if query.upper() in s["symbol"] or query.upper() in s["name"].upper()
        ]
    else:
        filtered = popular_symbols

    return {
        "symbols": filtered,
        "count": len(filtered),
    }
