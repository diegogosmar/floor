#!/bin/bash
# Run tests for OFP Floor Manager

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 OFP Floor Manager - Test Suite"
echo "=================================="
echo ""

# Detect Python command (check venv first, then python3/python)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
    echo "Using venv Python: $PYTHON_CMD"
elif [ -f "$SCRIPT_DIR/myenv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/myenv/bin/python"
    echo "Using myenv Python: $PYTHON_CMD"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found!${NC}"
    echo ""
    echo "Make sure Python 3.11+ is installed and in your PATH"
    echo "Or create a virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    exit 1
fi

# Check if pytest is installed (via python module)
if ! $PYTHON_CMD -c "import pytest" 2>/dev/null; then
    echo -e "${RED}❌ pytest not found!${NC}"
    echo ""
    echo "Install dependencies with:"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Or activate your virtual environment first:"
    echo "  source venv/bin/activate  # or your venv path"
    exit 1
fi

# Use python -m pytest instead of pytest directly (works with venv)
PYTEST_CMD="$PYTHON_CMD -m pytest"

# Check if pytest-asyncio is installed
if ! $PYTHON_CMD -c "import pytest_asyncio" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  pytest-asyncio not found${NC}"
    echo "Installing pytest-asyncio..."
    $PYTHON_CMD -m pip install pytest-asyncio>=0.23.0
fi

echo ""

# Run tests with different options based on arguments
if [ "$1" == "-v" ] || [ "$1" == "--verbose" ]; then
    echo "Running tests with verbose output..."
    $PYTEST_CMD -v
elif [ "$1" == "-c" ] || [ "$1" == "--coverage" ]; then
    echo "Running tests with coverage..."
    $PYTEST_CMD --cov=src --cov-report=html --cov-report=term
    echo ""
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
elif [ "$1" == "-f" ] || [ "$1" == "--floor" ]; then
    echo "Running floor manager tests only..."
    $PYTEST_CMD tests/test_floor_manager.py -v
elif [ "$1" == "-a" ] || [ "$1" == "--agents" ]; then
    echo "Running agent tests only..."
    $PYTEST_CMD tests/test_agents.py -v
elif [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: ./run_tests.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  (no args)    Run all tests"
    echo "  -v, --verbose    Run with verbose output"
    echo "  -c, --coverage  Run with coverage report"
    echo "  -f, --floor      Run floor manager tests only"
    echo "  -a, --agents    Run agent tests only"
    echo "  -h, --help       Show this help"
    exit 0
else
    echo "Running all tests..."
    $PYTEST_CMD
fi

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"

