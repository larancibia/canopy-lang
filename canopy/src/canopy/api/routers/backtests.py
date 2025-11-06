"""
Backtest Router - Endpoints for backtest operations.
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from canopy.api.models.requests import BacktestRequest
from canopy.api.models.responses import (
    BacktestJobResponse,
    BacktestStatusResponse,
    BacktestResultResponse,
)
from canopy.api.services.backtest_service import BacktestService
from canopy.api.services.job_queue import get_job_queue, JobStatus
from canopy.api.dependencies import get_data_provider

router = APIRouter(prefix="/backtests", tags=["backtests"])


@router.post("", response_model=BacktestJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_backtest(request: BacktestRequest):
    """
    Submit a backtest job.

    Creates a new backtest job and returns immediately with a job ID.
    The backtest runs asynchronously in the background.

    Example:
        ```
        POST /api/backtests
        {
            "strategy_code": "strategy \"MA Crossover\"\\n...",
            "symbol": "AAPL",
            "start_date": "2022-01-01T00:00:00Z",
            "end_date": "2023-12-31T23:59:59Z",
            "initial_capital": 10000.0
        }
        ```

    Returns:
        Job information with job_id for tracking
    """
    # Get job queue
    job_queue = get_job_queue()

    # Create backtest service
    data_provider = get_data_provider(request.data_provider)
    backtest_service = BacktestService(data_provider)

    # Submit job to queue
    job_id = await job_queue.submit(
        backtest_service.run_backtest,
        request.strategy_code,
        request.symbol,
        request.start_date,
        request.end_date,
        request.initial_capital,
        request.commission,
        request.slippage,
        metadata={
            "symbol": request.symbol,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "initial_capital": request.initial_capital,
        },
    )

    return BacktestJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Backtest job queued successfully",
    )


@router.get("/{job_id}", response_model=BacktestStatusResponse)
async def get_backtest_status(job_id: str):
    """
    Get backtest job status.

    Retrieves the current status of a backtest job, including progress
    information if the job is running.

    Args:
        job_id: Job identifier returned from POST /backtests

    Example:
        ```
        GET /api/backtests/bkt_abc123xyz
        ```
    """
    job_queue = get_job_queue()
    job = job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )

    return BacktestStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error,
    )


@router.get("/{job_id}/results", response_model=BacktestResultResponse)
async def get_backtest_results(job_id: str):
    """
    Get backtest results.

    Retrieves the complete results of a finished backtest job,
    including performance metrics, trades, and equity curve.

    Args:
        job_id: Job identifier

    Example:
        ```
        GET /api/backtests/bkt_abc123xyz/results
        ```

    Raises:
        404: If job not found
        400: If job not completed
    """
    job_queue = get_job_queue()
    job = job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed (status: {job.status.value})",
        )

    # Get results
    backtest, metrics = job.result

    # Format results
    backtest_service = BacktestService(get_data_provider())
    result = backtest_service.format_backtest_result(
        job_id=job.job_id,
        backtest=backtest,
        metrics=metrics,
        symbol=job.metadata.get("symbol", "UNKNOWN"),
        start_date=job.metadata.get("start_date"),
        end_date=job.metadata.get("end_date"),
        initial_capital=job.metadata.get("initial_capital", 10000.0),
    )

    return result


@router.delete("/{job_id}")
async def cancel_backtest(job_id: str):
    """
    Cancel a running backtest.

    Attempts to cancel a backtest job. Only pending jobs can be cancelled.
    Running jobs cannot be cancelled in this MVP implementation.

    Args:
        job_id: Job identifier

    Example:
        ```
        DELETE /api/backtests/bkt_abc123xyz
        ```
    """
    job_queue = get_job_queue()

    if not job_queue.get_job(job_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )

    cancelled = await job_queue.cancel_job(job_id)

    if cancelled:
        return {"message": f"Job {job_id} cancelled successfully", "cancelled": True}
    else:
        return {
            "message": f"Job {job_id} could not be cancelled (already running or completed)",
            "cancelled": False,
        }


@router.get("")
async def list_backtests(limit: int = 100):
    """
    List recent backtest jobs.

    Returns a list of recent backtest jobs with their status.

    Args:
        limit: Maximum number of jobs to return (default 100)

    Example:
        ```
        GET /api/backtests?limit=10
        ```
    """
    job_queue = get_job_queue()
    jobs = job_queue.list_jobs(limit=limit)

    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "metadata": job.metadata,
            }
            for job in jobs
        ],
        "count": len(jobs),
    }
