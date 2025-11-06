"""
Error Handler Middleware - Global error handling.
"""

from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handler middleware.

    Catches and formats exceptions into consistent JSON responses.

    Args:
        request: FastAPI request
        call_next: Next middleware or endpoint

    Returns:
        Response with error details if exception occurred
    """
    try:
        return await call_next(request)
    except Exception as exc:
        # Log the error (in production, use proper logging)
        print(f"Unhandled exception: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


def setup_exception_handlers(app):
    """
    Setup custom exception handlers for the FastAPI app.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "detail": exc.errors(),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid request",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        # Log the error (in production, use proper logging)
        print(f"Unhandled exception: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
