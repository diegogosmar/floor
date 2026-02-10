#!/bin/bash
# Script per lanciare le GUI Streamlit

set -e

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Floor Manager GUI Launcher${NC}"
echo ""

# Verifica che siamo nella directory corretta
if [ ! -f "streamlit_app.py" ]; then
    echo -e "${YELLOW}⚠️  File streamlit_app.py non trovato!${NC}"
    echo "Assicurati di essere nella directory del progetto."
    exit 1
fi

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
    echo -e "${RED}❌ Python non trovato!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Usando Python: $PYTHON_CMD${NC}"
echo ""

# Menu di selezione
echo "Quale GUI vuoi lanciare?"
echo ""
echo "1) Standard GUI (streamlit_app.py) - Consigliata per iniziare"
echo "2) Real-Time GUI (streamlit_app_realtime.py) - Con aggiornamenti automatici"
echo "3) Entrambe (porta 8501 e 8502)"
echo "4) Solo Floor Manager (senza GUI)"
echo ""
read -p "Scegli un'opzione [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 Avvio Standard GUI...${NC}"
        echo ""
        echo "📝 Comandi manuali:"
        echo "   Terminal 1: docker-compose up"
        echo "   Terminal 2: $STREAMLIT_CMD run streamlit_app.py"
        echo ""
        echo "⚠️  Assicurati che Floor Manager sia già avviato!"
        echo ""
        read -p "Premi INVIO per continuare..."
        $STREAMLIT_CMD run streamlit_app.py
        ;;
    2)
        echo ""
        echo -e "${GREEN}⚡ Avvio Real-Time GUI...${NC}"
        echo ""
        echo "📝 Comandi manuali:"
        echo "   Terminal 1: docker-compose up"
        echo "   Terminal 2: $STREAMLIT_CMD run streamlit_app_realtime.py"
        echo ""
        echo "⚠️  Assicurati che Floor Manager sia già avviato!"
        echo ""
        read -p "Premi INVIO per continuare..."
        $STREAMLIT_CMD run streamlit_app_realtime.py
        ;;
    3)
        echo ""
        echo -e "${GREEN}🚀 Avvio entrambe le GUI...${NC}"
        echo ""
        echo "📝 Comandi manuali:"
        echo "   Terminal 1: docker-compose up"
        echo "   Terminal 2: $STREAMLIT_CMD run streamlit_app.py --server.port 8501"
        echo "   Terminal 3: $STREAMLIT_CMD run streamlit_app_realtime.py --server.port 8502"
        echo ""
        echo "⚠️  Assicurati che Floor Manager sia già avviato!"
        echo ""
        read -p "Premi INVIO per continuare..."
        echo ""
        echo -e "${BLUE}Avvio Standard GUI su porta 8501...${NC}"
        $STREAMLIT_CMD run streamlit_app.py --server.port 8501 &
        PID1=$!
        sleep 2
        echo -e "${BLUE}Avvio Real-Time GUI su porta 8502...${NC}"
        $STREAMLIT_CMD run streamlit_app_realtime.py --server.port 8502 &
        PID2=$!
        echo ""
        echo -e "${GREEN}✅ Entrambe le GUI sono avviate!${NC}"
        echo "   Standard: http://localhost:8501"
        echo "   Real-Time: http://localhost:8502"
        echo ""
        echo "Premi Ctrl+C per fermare entrambe..."
        wait $PID1 $PID2
        ;;
    4)
        echo ""
        echo -e "${GREEN}🐳 Avvio solo Floor Manager...${NC}"
        echo ""
        docker-compose up
        ;;
    *)
        echo ""
        echo -e "${YELLOW}❌ Opzione non valida!${NC}"
        exit 1
        ;;
esac


