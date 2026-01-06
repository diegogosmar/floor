#!/bin/bash
# Script rapido per lanciare Real-Time GUI

echo "⚡ Avvio Real-Time GUI..."
echo ""
echo "⚠️  Assicurati che Floor Manager sia già avviato (docker-compose up)"
echo ""
streamlit run streamlit_app_realtime.py

