"""
Auth Middleware - API key authentication (basic implementation).
"""

from fastapi import Request, HTTPException, status
from canopy.api.config import settings


async def api_key_middleware(request: Request, call_next):
    """
    API key authentication middleware.

    Validates API key from X-API-Key header.

    Args:
        request: FastAPI request
        call_next: Next middleware or endpoint

    Returns:
        Response from next middleware/endpoint

    Raises:
        HTTPException: If API key is invalid
    """
    # Skip authentication if disabled
    if not settings.enable_auth:
        return await call_next(request)

    # Skip for docs endpoints
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return await call_next(request)

    # Get API key from header
    api_key = request.headers.get("X-API-Key")

    # Validate API key
    if not api_key or api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Continue to next middleware/endpoint
    return await call_next(request)
