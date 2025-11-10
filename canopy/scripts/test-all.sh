#!/bin/bash
# Run all tests and quality checks

set -e

echo "🧪 Running all tests and quality checks..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Function to run command and track failures
run_check() {
    local name=$1
    local command=$2

    echo ""
    echo "========================================="
    echo "Running: $name"
    echo "========================================="

    if eval "$command"; then
        echo -e "${GREEN}✓ $name passed${NC}"
    else
        echo -e "${RED}✗ $name failed${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# 1. Code formatting check
run_check "Black (formatting)" "poetry run black --check src/ tests/"

# 2. Import sorting check
run_check "isort (import sorting)" "poetry run isort --check-only src/ tests/"

# 3. Linting
run_check "flake8 (linting)" "poetry run flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503"

# 4. Type checking
run_check "mypy (type checking)" "poetry run mypy src/"

# 5. Unit tests
run_check "Unit tests" "poetry run pytest tests/unit -v --tb=short"

# 6. Integration tests
run_check "Integration tests" "poetry run pytest tests/integration -v --tb=short"

# 7. Coverage
run_check "Test coverage" "poetry run pytest --cov=src/canopy --cov-report=term --cov-report=html --cov-fail-under=80"

# 8. Security check (if bandit is installed)
if poetry run which bandit &> /dev/null; then
    run_check "Security check (bandit)" "poetry run bandit -r src/ -ll"
fi

# Summary
echo ""
echo "========================================="
echo "Summary"
echo "========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED check(s) failed${NC}"
    echo ""
    echo "To fix formatting issues automatically, run:"
    echo "  poetry run black src/ tests/"
    echo "  poetry run isort src/ tests/"
    exit 1
fi
