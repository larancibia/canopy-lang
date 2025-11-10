#!/bin/bash
# Run development servers for API and web frontend

echo "🚀 Starting Canopy development servers..."

# Check if running in tmux or screen
if [ -z "$TMUX" ] && [ -z "$STY" ]; then
    echo "⚠️  Tip: Consider running this in tmux or screen for better management"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $API_PID 2>/dev/null
    kill $WEB_PID 2>/dev/null
    kill $REDIS_PID 2>/dev/null
    echo "✓ Servers stopped"
    exit 0
}

trap cleanup EXIT INT TERM

# Start Redis (if Docker is available)
if command -v docker &> /dev/null; then
    echo "Starting Redis..."
    docker run --rm -d --name canopy-redis -p 6379:6379 redis:7-alpine &> /dev/null || true
    REDIS_PID=$!
    sleep 2
    echo "✓ Redis started on port 6379"
else
    echo "⚠️  Docker not found. Make sure Redis is running on port 6379"
fi

# Start API server
echo ""
echo "Starting API server..."
poetry run uvicorn canopy.api.main:app --reload --port 8000 &
API_PID=$!
sleep 2
echo "✓ API server started on http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"

# Start web frontend (if exists)
if [ -d "web" ]; then
    echo ""
    echo "Starting web frontend..."
    cd web
    npm run dev &
    WEB_PID=$!
    cd ..
    sleep 2
    echo "✓ Web frontend started on http://localhost:5173"
else
    echo "⚠️  Web directory not found. Skipping frontend."
fi

echo ""
echo "========================================="
echo "✅ Development servers running"
echo "========================================="
echo ""
echo "Services:"
echo "  API:      http://localhost:8000"
echo "  Docs:     http://localhost:8000/docs"
echo "  Web:      http://localhost:5173"
echo "  Redis:    localhost:6379"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for all background processes
wait
