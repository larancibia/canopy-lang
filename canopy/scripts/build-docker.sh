#!/bin/bash
# Build Docker images for Canopy

set -e

echo "🐳 Building Docker images..."

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "Version: $VERSION"

# Build API image
echo ""
echo "Building API image..."
docker build -t canopy-api:latest -t canopy-api:$VERSION --target production .
echo "✓ API image built: canopy-api:latest, canopy-api:$VERSION"

# Build web image (if web directory exists)
if [ -d "web" ]; then
    echo ""
    echo "Building web frontend image..."
    docker build -t canopy-web:latest -t canopy-web:$VERSION --target production -f web/Dockerfile web/
    echo "✓ Web image built: canopy-web:latest, canopy-web:$VERSION"
fi

# Test images
echo ""
echo "Testing images..."

# Test API
echo "Testing API image..."
if docker run --rm canopy-api:latest poetry run python -c "import canopy; print('✓ API image works')"; then
    echo "✓ API image test passed"
else
    echo "✗ API image test failed"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ Docker images built successfully"
echo "========================================="
echo ""
echo "Images:"
echo "  canopy-api:latest"
echo "  canopy-api:$VERSION"
if [ -d "web" ]; then
    echo "  canopy-web:latest"
    echo "  canopy-web:$VERSION"
fi
echo ""
echo "To run with Docker Compose:"
echo "  docker-compose up"
echo ""
echo "To push to registry:"
echo "  docker tag canopy-api:latest your-registry/canopy-api:$VERSION"
echo "  docker push your-registry/canopy-api:$VERSION"
