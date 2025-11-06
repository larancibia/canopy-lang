#!/bin/bash
# Setup script for Canopy development environment

set -e  # Exit on error

echo "🚀 Setting up Canopy development environment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux or Mac
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✓ OS detected: $OSTYPE"
else
    echo "⚠️  Warning: Unsupported OS. This script is designed for Linux/Mac."
fi

# Check Python version
echo ""
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python $PYTHON_VERSION found"

    # Check if version is 3.11+
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; then
        echo "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Install Poetry if not installed
echo ""
echo "Checking Poetry..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "✓ Poetry installed"
else
    echo "✓ Poetry found: $(poetry --version)"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
poetry install
echo "✓ Python dependencies installed"

# Check if Node.js is installed (for web frontend)
echo ""
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js $NODE_VERSION found"

    # Install frontend dependencies
    if [ -d "web" ]; then
        echo "Installing frontend dependencies..."
        cd web
        npm install
        cd ..
        echo "✓ Frontend dependencies installed"
    fi
else
    echo "⚠️  Node.js not found. Skipping frontend setup."
    echo "   Install Node.js 18+ to develop the web frontend."
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please update .env with your configuration"
else
    echo "✓ .env file already exists"
fi

# Install pre-commit hooks (if available)
echo ""
if poetry run which pre-commit &> /dev/null; then
    echo "Installing pre-commit hooks..."
    poetry run pre-commit install
    echo "✓ Pre-commit hooks installed"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p backups
echo "✓ Directories created"

# Check Docker (optional)
echo ""
if command -v docker &> /dev/null; then
    echo "✓ Docker found: $(docker --version)"
    if command -v docker-compose &> /dev/null; then
        echo "✓ Docker Compose found: $(docker-compose --version)"
    fi
else
    echo "⚠️  Docker not found. Docker is optional but recommended."
fi

# Run tests to verify installation
echo ""
echo "Running tests to verify installation..."
if poetry run pytest tests/unit --maxfail=1 -q; then
    echo "✓ Tests passed"
else
    echo "⚠️  Some tests failed. Please check your setup."
fi

echo ""
echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Update .env with your configuration"
echo "  2. Run the dev server: ./scripts/run-dev.sh"
echo "  3. Run tests: ./scripts/test-all.sh"
echo "  4. View docs: open docs/DEVELOPMENT.md"
echo ""
echo "Happy coding! 🎉"
