"""
API Dependencies - Shared dependencies for dependency injection.
"""

from typing import Optional
from fastapi import Header, HTTPException, status
from canopy.api.config import settings
from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.ports.data_provider import IDataProvider
from canopy.ports.backtest_engine import IBacktestEngine


def get_data_provider(provider: Optional[str] = None) -> IDataProvider:
    """
    Get data provider instance.

    Args:
        provider: Provider type (defaults to configured default)

    Returns:
        IDataProvider instance
    """
    provider_type = provider or settings.default_data_provider
    return DataProviderFactory.create(provider_type)


def get_backtest_engine() -> IBacktestEngine:
    """
    Get backtest engine instance.

    Returns:
        IBacktestEngine instance
    """
    return SimpleBacktestEngine()


def get_backtest_use_case(
    engine: IBacktestEngine = None,
) -> RunBacktestUseCase:
    """
    Get backtest use case instance.

    Args:
        engine: Optional backtest engine (will create if not provided)

    Returns:
        RunBacktestUseCase instance
    """
    if engine is None:
        engine = get_backtest_engine()
    return RunBacktestUseCase(engine)


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key for protected endpoints.

    Args:
        x_api_key: API key from request header

    Returns:
        Verified API key

    Raises:
        HTTPException: If API key is invalid
    """
    if not settings.enable_auth:
        return "dev-mode"

    if not x_api_key or x_api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key
