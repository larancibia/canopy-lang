# Multi-stage build for Canopy API
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Add poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Development stage
FROM base as development
RUN poetry install --no-root
COPY . .
RUN poetry install
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "canopy.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production
RUN poetry install --no-dev --no-root
COPY . .
RUN poetry install --no-dev

# Create non-root user
RUN useradd -m -u 1000 canopy && chown -R canopy:canopy /app
USER canopy

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "canopy.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
