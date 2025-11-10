"""
Data Router - Endpoints for market data operations.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from canopy.api.models.responses import (
    DataProviderResponse,
    OHLCVResponse,
    SymbolSearchResponse,
)
from canopy.api.models.schemas import OHLCVData
from canopy.api.services.data_service import DataService
from canopy.api.dependencies import get_data_provider
from canopy.api.config import settings

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/providers", response_model=DataProviderResponse)
async def get_providers():
    """
    Get available data providers.

    Returns a list of available data providers that can be used
    for fetching market data.

    Example:
        ```
        GET /api/data/providers
        ```
    """
    data_service = DataService()
    providers = data_service.get_available_providers()

    return DataProviderResponse(
        providers=providers, default=settings.default_data_provider
    )


@router.get("/symbols", response_model=SymbolSearchResponse)
async def search_symbols(
    q: str = Query(..., description="Search query", min_length=1)
):
    """
    Search for trading symbols.

    Returns a list of symbols matching the search query.

    Args:
        q: Search query (e.g., "AAPL", "MSFT")

    Example:
        ```
        GET /api/data/symbols?q=AAPL
        ```
    """
    data_service = DataService()
    results = data_service.search_symbols(q)

    return SymbolSearchResponse(query=q, results=results, count=len(results))


@router.get("/{symbol}/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str,
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    provider: str = Query(None, description="Data provider to use"),
):
    """
    Get OHLCV historical data for a symbol.

    Fetches Open, High, Low, Close, Volume data for the specified symbol
    and date range.

    Args:
        symbol: Trading symbol (e.g., "AAPL")
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        provider: Optional data provider (defaults to configured provider)

    Example:
        ```
        GET /api/data/AAPL/ohlcv?start_date=2022-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z
        ```
    """
    try:
        data_provider = get_data_provider(provider)
        data_service = DataService(data_provider)

        # Fetch data
        timeseries = data_service.get_ohlcv_data(symbol, start_date, end_date)

        # Convert to response format
        data_list = data_service.timeseries_to_dict(timeseries)
        ohlcv_data = [OHLCVData(**item) for item in data_list]

        return OHLCVResponse(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            data=ohlcv_data,
            count=len(ohlcv_data),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch data: {str(e)}",
        )
