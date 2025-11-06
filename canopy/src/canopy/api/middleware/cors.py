"""
CORS Middleware - Cross-Origin Resource Sharing configuration.
"""

from fastapi.middleware.cors import CORSMiddleware
from canopy.api.config import settings


def setup_cors(app):
    """
    Setup CORS middleware for the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
