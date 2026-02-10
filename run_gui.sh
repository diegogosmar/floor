#!/bin/bash
# Script to launch Streamlit GUIs

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Floor Manager GUI Launcher${NC}"
echo ""

# Verify we're in the correct directory
if [ ! -f "streamlit_app.py" ]; then
    echo -e "${YELLOW}⚠️  File streamlit_app.py not found!${NC}"
    echo "Make sure you're in the project directory."
    exit 1
fi

# Detect Python from venv
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
    STREAMLIT_CMD="$PYTHON_CMD -m streamlit"
elif [ -f "$SCRIPT_DIR/myenv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/myenv/bin/python"
    STREAMLIT_CMD="$PYTHON_CMD -m streamlit"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    STREAMLIT_CMD="$PYTHON_CMD -m streamlit"
else
    echo -e "${RED}❌ Python not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Using Python: $PYTHON_CMD${NC}"
echo ""

# Selection menu
echo "Which GUI do you want to launch?"
echo ""
echo "1) Standard GUI (streamlit_app.py) - Recommended to start"
echo "2) Real-Time GUI (streamlit_app_realtime.py) - With automatic updates"
echo "3) Both (port 8501 and 8502)"
echo "4) Floor Manager only (no GUI)"
echo ""
read -p "Choose an option [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 Starting Standard GUI...${NC}"
        echo ""
        echo "📝 Manual commands:"
        echo "   Terminal 1: docker-compose up"
        echo "   Terminal 2: $STREAMLIT_CMD run streamlit_app.py"
        echo ""
        echo "⚠️  Make sure Floor Manager is already running!"
        echo ""
        read -p "Press ENTER to continue..."
        $STREAMLIT_CMD run streamlit_app.py
        ;;
    2)
        echo ""
        echo -e "${GREEN}⚡ Starting Real-Time GUI...${NC}"
        echo ""
        echo "📝 Manual commands:"
        echo "   Terminal 1: docker-compose up"
        echo "   Terminal 2: $STREAMLIT_CMD run streamlit_app_realtime.py"
        echo ""
        echo "⚠️  Make sure Floor Manager is already running!"
        echo ""
        read -p "Press ENTER to continue..."
        $STREAMLIT_CMD run streamlit_app_realtime.py
        ;;
    3)
        echo ""
        echo -e "${GREEN}🚀 Starting both GUIs...${NC}"
        echo ""
        echo "📝 Manual commands:"
        echo "   Terminal 1: docker-compose up"
        echo "   Terminal 2: $STREAMLIT_CMD run streamlit_app.py --server.port 8501"
        echo "   Terminal 3: $STREAMLIT_CMD run streamlit_app_realtime.py --server.port 8502"
        echo ""
        echo "⚠️  Make sure Floor Manager is already running!"
        echo ""
        read -p "Press ENTER to continue..."
        echo ""
        echo -e "${BLUE}Starting Standard GUI on port 8501...${NC}"
        $STREAMLIT_CMD run streamlit_app.py --server.port 8501 &
        PID1=$!
        sleep 2
        echo -e "${BLUE}Starting Real-Time GUI on port 8502...${NC}"
        $STREAMLIT_CMD run streamlit_app_realtime.py --server.port 8502 &
        PID2=$!
        echo ""
        echo -e "${GREEN}✅ Both GUIs are running!${NC}"
        echo "   Standard: http://localhost:8501"
        echo "   Real-Time: http://localhost:8502"
        echo ""
        echo "Press Ctrl+C to stop both..."
        wait $PID1 $PID2
        ;;
    4)
        echo ""
        echo -e "${GREEN}🐳 Starting Floor Manager only...${NC}"
        echo ""
        docker-compose up
        ;;
    *)
        echo ""
        echo -e "${YELLOW}❌ Invalid option!${NC}"
        exit 1
        ;;
esac


