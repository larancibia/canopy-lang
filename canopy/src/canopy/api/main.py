"""
Main FastAPI Application - Canopy Trading Language API.

This module sets up the FastAPI application with all routes, middleware,
and configuration for the Canopy trading language REST API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from canopy.api.config import settings
from canopy.api.routers import strategies, backtests, data, indicators
from canopy.api.middleware.cors import setup_cors
from canopy.api.middleware.error_handler import setup_exception_handlers
from canopy.api.services.job_queue import get_job_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup: Start the job queue
    job_queue = get_job_queue()
    await job_queue.start()
    print("✓ Job queue started")

    yield

    # Shutdown: Stop the job queue
    await job_queue.stop()
    print("✓ Job queue stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Canopy Trading Language API - A REST API for developing, testing, and running trading strategies.

    ## Features

    * **Strategy Management**: Parse, validate, and manage trading strategies written in Canopy DSL
    * **Backtesting**: Run backtests asynchronously with comprehensive performance metrics
    * **Market Data**: Fetch historical OHLCV data from multiple providers
    * **Technical Indicators**: Calculate and use technical indicators (SMA, EMA, RSI, etc.)

    ## Authentication

    Authentication is currently disabled for MVP. In production, use the `X-API-Key` header.

    ## Rate Limiting

    Rate limiting is currently disabled for MVP.

    ## Getting Started

    1. Parse a strategy: `POST /api/strategies/parse`
    2. Submit a backtest: `POST /api/backtests`
    3. Check status: `GET /api/backtests/{job_id}`
    4. Get results: `GET /api/backtests/{job_id}/results`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup CORS
setup_cors(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(strategies.router, prefix=settings.api_prefix)
app.include_router(backtests.router, prefix=settings.api_prefix)
app.include_router(data.router, prefix=settings.api_prefix)
app.include_router(indicators.router, prefix=settings.api_prefix)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns the API health status and version information.

    Example:
        ```
        GET /health
        ```
    """
    job_queue = get_job_queue()
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.app_version,
            "job_queue": {
                "running": job_queue.running,
                "workers": len(job_queue.workers),
                "queue_size": job_queue.queue.qsize(),
                "total_jobs": len(job_queue.jobs),
            },
        }
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.

    Returns basic API information and links to documentation.

    Example:
        ```
        GET /
        ```
    """
    return JSONResponse(
        content={
            "message": "Canopy Trading Language API",
            "version": settings.app_version,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "canopy.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
