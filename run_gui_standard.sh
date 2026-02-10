#!/bin/bash
# Quick script to launch Standard GUI

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
    echo "❌ Python not found!"
    exit 1
fi

echo "🚀 Starting Standard GUI..."
echo "✓ Using Python: $PYTHON_CMD"
echo ""
echo "⚠️  Make sure Floor Manager is already running (docker-compose up)"
echo ""
$STREAMLIT_CMD run streamlit_app.py


