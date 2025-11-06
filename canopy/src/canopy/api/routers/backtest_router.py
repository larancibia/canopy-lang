"""
Backtest Router - Endpoints for running and managing backtests.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from canopy.parser.parser import CanopyParser
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine

router = APIRouter()

# In-memory job storage (replace with Redis in production)
backtest_jobs: Dict[str, Dict[str, Any]] = {}


class BacktestRequest(BaseModel):
    """Request model for running a backtest."""

    strategy_code: str = Field(..., description="Canopy strategy code")
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(10000.0, description="Initial capital")
    commission: float = Field(0.001, description="Commission rate (e.g., 0.001 = 0.1%)")
    provider: str = Field("yahoo", description="Data provider (yahoo, csv)")


class BacktestResponse(BaseModel):
    """Response model for backtest submission."""

    job_id: str
    status: str
    message: str


class BacktestResultResponse(BaseModel):
    """Response model for backtest results."""

    job_id: str
    status: str
    strategy_name: str | None = None
    symbol: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    metrics: Dict[str, Any] | None = None
    trades: List[Dict[str, Any]] | None = None
    equity_curve: List[Dict[str, Any]] | None = None
    error: str | None = None


async def run_backtest_job(job_id: str, request: BacktestRequest):
    """Background task to run a backtest."""
    try:
        backtest_jobs[job_id]["status"] = "running"
        backtest_jobs[job_id]["started_at"] = datetime.utcnow().isoformat()

        # Parse strategy
        parser = CanopyParser()
        strategy = parser.parse(request.strategy_code)

        # Create data provider
        provider = DataProviderFactory.create(request.provider)

        # Create backtest engine
        engine = SimpleBacktestEngine()

        # Run backtest
        use_case = RunBacktestUseCase(provider, engine)
        result = use_case.execute(
            strategy=strategy,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            commission=request.commission,
        )

        # Store results
        backtest_jobs[job_id]["status"] = "completed"
        backtest_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        backtest_jobs[job_id]["result"] = {
            "strategy_name": strategy.name,
            "symbol": request.symbol,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "metrics": {
                "total_return": result.metrics.total_return,
                "sharpe_ratio": result.metrics.sharpe_ratio,
                "sortino_ratio": result.metrics.sortino_ratio,
                "max_drawdown": result.metrics.max_drawdown,
                "win_rate": result.metrics.win_rate,
                "profit_factor": result.metrics.profit_factor,
                "total_trades": result.metrics.total_trades,
            },
            "trades": [
                {
                    "entry_date": trade.entry_date.isoformat(),
                    "exit_date": trade.exit_date.isoformat(),
                    "entry_price": trade.entry_price,
                    "exit_price": trade.exit_price,
                    "shares": trade.shares,
                    "pnl": trade.pnl,
                    "return_pct": trade.return_pct,
                }
                for trade in result.trades
            ],
            "equity_curve": [
                {
                    "date": point.timestamp.isoformat(),
                    "equity": point.value,
                }
                for point in result.equity_curve
            ],
        }

    except Exception as e:
        backtest_jobs[job_id]["status"] = "failed"
        backtest_jobs[job_id]["error"] = str(e)
        backtest_jobs[job_id]["failed_at"] = datetime.utcnow().isoformat()


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest, background_tasks: BackgroundTasks
) -> BacktestResponse:
    """
    Submit a backtest job.

    Args:
        request: Backtest configuration
        background_tasks: FastAPI background tasks

    Returns:
        Job ID and status
    """
    job_id = str(uuid.uuid4())

    # Initialize job
    backtest_jobs[job_id] = {
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "request": request.dict(),
    }

    # Add background task
    background_tasks.add_task(run_backtest_job, job_id, request)

    return BacktestResponse(
        job_id=job_id,
        status="pending",
        message="Backtest job submitted successfully",
    )


@router.get("/{job_id}", response_model=BacktestResultResponse)
async def get_backtest_result(job_id: str) -> BacktestResultResponse:
    """
    Get backtest results by job ID.

    Args:
        job_id: Backtest job ID

    Returns:
        Backtest results or status
    """
    if job_id not in backtest_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = backtest_jobs[job_id]

    if job["status"] == "completed":
        result = job["result"]
        return BacktestResultResponse(
            job_id=job_id,
            status="completed",
            strategy_name=result["strategy_name"],
            symbol=result["symbol"],
            start_date=result["start_date"],
            end_date=result["end_date"],
            metrics=result["metrics"],
            trades=result["trades"],
            equity_curve=result["equity_curve"],
        )
    elif job["status"] == "failed":
        return BacktestResultResponse(
            job_id=job_id,
            status="failed",
            error=job.get("error", "Unknown error"),
        )
    else:
        return BacktestResultResponse(
            job_id=job_id,
            status=job["status"],
        )


@router.get("/")
async def list_backtests() -> Dict[str, Any]:
    """
    List all backtest jobs.

    Returns:
        List of backtest jobs
    """
    jobs = []
    for job_id, job in backtest_jobs.items():
        jobs.append(
            {
                "job_id": job_id,
                "status": job["status"],
                "created_at": job["created_at"],
            }
        )

    return {
        "jobs": jobs,
        "count": len(jobs),
    }


@router.delete("/{job_id}")
async def delete_backtest(job_id: str) -> Dict[str, Any]:
    """
    Delete a backtest job.

    Args:
        job_id: Backtest job ID

    Returns:
        Deletion confirmation
    """
    if job_id not in backtest_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del backtest_jobs[job_id]

    return {
        "message": "Backtest deleted successfully",
        "job_id": job_id,
    }
