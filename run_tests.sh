#!/bin/bash
# Run tests for OFP Floor Manager

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🧪 OFP Floor Manager - Test Suite"
echo "=================================="
echo ""

# Detect Python command (check venv first, then python3/python)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
elif [ -f "$SCRIPT_DIR/myenv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/myenv/bin/python"
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

# If arguments provided, use direct mode (backward compatibility)
if [ "$1" != "" ] && [ "$1" != "-i" ] && [ "$1" != "--interactive" ]; then
    case "$1" in
        -v|--verbose)
            echo "Running tests with verbose output..."
            $PYTEST_CMD -v
            ;;
        -c|--coverage)
            echo "Running tests with coverage..."
            $PYTEST_CMD --cov=src --cov-report=html --cov-report=term
            echo ""
            echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
            ;;
        -f|--floor)
            echo "Running floor manager tests only..."
            $PYTEST_CMD tests/test_floor_manager.py -v
            ;;
        -a|--agents)
            echo "Running agent tests only..."
            $PYTEST_CMD tests/test_agents.py -v
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no args)    Interactive menu"
            echo "  -i, --interactive    Interactive menu"
            echo "  -v, --verbose    Run all tests with verbose output"
            echo "  -c, --coverage  Run all tests with coverage report"
            echo "  -f, --floor      Run floor manager tests only"
            echo "  -a, --agents     Run agent tests only"
            echo "  -h, --help       Show this help"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
    echo ""
    echo -e "${GREEN}✅ Tests completed!${NC}"
    exit 0
fi

# Interactive menu mode
echo -e "${BLUE}Quale test vuoi eseguire?${NC}"
echo ""
echo "1) Tutti i test (pytest)"
echo "2) Test Floor Manager"
echo "3) Test Agenti"
echo "4) Test con coverage report"
echo "5) Test Streamlit GUI"
echo "6) Test WebSocket/SSE endpoint"
echo ""
read -p "Scegli un'opzione [1-6]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🧪 Esecuzione di tutti i test...${NC}"
        echo ""
        $PYTEST_CMD -v
        ;;
    2)
        echo ""
        echo -e "${GREEN}🧪 Esecuzione test Floor Manager...${NC}"
        echo ""
        $PYTEST_CMD tests/test_floor_manager.py -v
        ;;
    3)
        echo ""
        echo -e "${GREEN}🧪 Esecuzione test Agenti...${NC}"
        echo ""
        $PYTEST_CMD tests/test_agents.py -v
        ;;
    4)
        echo ""
        echo -e "${GREEN}🧪 Esecuzione test con coverage...${NC}"
        echo ""
        $PYTEST_CMD --cov=src --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    5)
        echo ""
        echo -e "${GREEN}🧪 Test Streamlit GUI...${NC}"
        echo ""
        if [ -f "test_streamlit.sh" ]; then
            ./test_streamlit.sh
        else
            echo -e "${YELLOW}⚠️  test_streamlit.sh non trovato!${NC}"
            echo ""
            echo "Verifica manualmente:"
            echo "  1. Avvia Floor Manager: docker-compose up"
            echo "  2. Avvia Streamlit: streamlit run streamlit_app.py"
        fi
        ;;
    6)
        echo ""
        echo -e "${GREEN}🧪 Test WebSocket/SSE endpoint...${NC}"
        echo ""
        echo "Verifica che Floor Manager sia avviato (docker-compose up)"
        echo ""
        
        # Test health endpoint
        echo "1️⃣ Testing health endpoint..."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Floor Manager is running${NC}"
        else
            echo -e "${RED}   ❌ Floor Manager is NOT running!${NC}"
            echo "   Start it with: docker-compose up"
            exit 1
        fi
        
        # Test SSE endpoint
        echo ""
        echo "2️⃣ Testing SSE endpoint..."
        if curl -s -N --max-time 2 http://localhost:8000/api/v1/events/floor/test_001 2>&1 | head -1 | grep -q "data:"; then
            echo -e "${GREEN}   ✅ SSE endpoint is working${NC}"
        else
            echo -e "${YELLOW}   ⚠️  SSE endpoint might not be working (check manually)${NC}"
        fi
        
        # Test WebSocket endpoint (basic check)
        echo ""
        echo "3️⃣ WebSocket endpoint available at:"
        echo "   ws://localhost:8000/api/v1/ws/floor/test_001"
        echo ""
        echo -e "${GREEN}✅ WebSocket/SSE tests completed!${NC}"
        ;;
    *)
        echo ""
        echo -e "${YELLOW}❌ Opzione non valida!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"
