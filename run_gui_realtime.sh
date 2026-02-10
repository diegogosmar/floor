#!/bin/bash
# Script rapido per lanciare Real-Time GUI

# Rileva Python dal venv
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
    echo "❌ Python non trovato!"
    exit 1
fi

echo "⚡ Avvio Real-Time GUI..."
echo "✓ Usando Python: $PYTHON_CMD"
echo ""
echo "⚠️  Assicurati che Floor Manager sia già avviato (docker-compose up)"
echo ""
$STREAMLIT_CMD run streamlit_app_realtime.py


