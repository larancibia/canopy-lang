"""
Job Queue - Background job processing for backtests.

This module implements an in-memory job queue for MVP.
In production, this would use Redis or a proper message queue.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BacktestJob:
    """Represents a backtest job."""

    job_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    message: str = "Job queued"
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class JobQueue:
    """
    In-memory job queue for background task processing.

    This is a simple implementation for MVP. In production, use:
    - Redis with RQ or Celery
    - AWS SQS
    - RabbitMQ
    - etc.
    """

    def __init__(self, max_workers: int = 5):
        """
        Initialize the job queue.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.jobs: Dict[str, BacktestJob] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.workers: list = []
        self.running = False

    async def start(self):
        """Start the job queue workers."""
        if self.running:
            return

        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(i)) for i in range(self.max_workers)
        ]

    async def stop(self):
        """Stop the job queue workers."""
        self.running = False
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)

    async def _worker(self, worker_id: int):
        """
        Worker coroutine to process jobs from the queue.

        Args:
            worker_id: Worker identifier
        """
        while self.running:
            try:
                # Get job from queue with timeout
                job_id, func, args, kwargs = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )

                job = self.jobs[job_id]
                job.status = JobStatus.RUNNING
                job.started_at = datetime.utcnow()
                job.message = "Running backtest..."

                try:
                    # Execute the job function
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = await asyncio.to_thread(func, *args, **kwargs)

                    # Mark job as completed
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.utcnow()
                    job.progress = 100.0
                    job.message = "Backtest completed successfully"
                    job.result = result

                except Exception as e:
                    # Mark job as failed
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.utcnow()
                    job.message = "Backtest failed"
                    job.error = str(e)

                finally:
                    self.queue.task_done()

            except asyncio.TimeoutError:
                # No job available, continue waiting
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")

    async def submit(
        self, func: Callable, *args, metadata: Optional[Dict[str, Any]] = None, **kwargs
    ) -> str:
        """
        Submit a job to the queue.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            metadata: Optional metadata for the job
            **kwargs: Keyword arguments for the function

        Returns:
            Job ID
        """
        # Generate unique job ID
        job_id = f"bkt_{uuid.uuid4().hex[:12]}"

        # Create job
        job = BacktestJob(
            job_id=job_id, metadata=metadata or {}, message="Job queued successfully"
        )
        self.jobs[job_id] = job

        # Add to queue
        await self.queue.put((job_id, func, args, kwargs))

        return job_id

    def get_job(self, job_id: str) -> Optional[BacktestJob]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            BacktestJob or None if not found
        """
        return self.jobs.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Note: In this simple implementation, we can only cancel pending jobs.
        Running jobs cannot be cancelled gracefully.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled, False otherwise
        """
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            job.message = "Job cancelled by user"
            return True

        return False

    def list_jobs(self, limit: int = 100) -> list[BacktestJob]:
        """
        List recent jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of jobs, sorted by creation time (newest first)
        """
        jobs = sorted(self.jobs.values(), key=lambda j: j.created_at, reverse=True)
        return jobs[:limit]


# Global job queue instance
_job_queue: Optional[JobQueue] = None


def get_job_queue() -> JobQueue:
    """
    Get the global job queue instance.

    Returns:
        JobQueue instance
    """
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue(max_workers=5)
    return _job_queue
