#!/bin/bash
# Quick test script for Streamlit GUIs

echo "🧪 Testing Streamlit GUI Applications"
echo ""

# Check if Floor Manager is running
echo "1️⃣ Checking Floor Manager..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Floor Manager is running"
else
    echo "   ❌ Floor Manager is NOT running"
    echo "   Start it with: docker-compose up"
    exit 1
fi

# Test SSE endpoint
echo ""
echo "2️⃣ Testing SSE endpoint..."
if curl -s -N --max-time 2 http://localhost:8000/api/v1/events/floor/test_001 2>&1 | head -1 | grep -q "data:"; then
    echo "   ✅ SSE endpoint is working"
else
    echo "   ⚠️  SSE endpoint might not be working (check manually)"
fi

# Check Streamlit
echo ""
echo "3️⃣ Checking Streamlit installation..."
if command -v streamlit &> /dev/null; then
    echo "   ✅ Streamlit is installed"
    streamlit --version
else
    echo "   ❌ Streamlit is NOT installed"
    echo "   Install with: pip install streamlit"
    exit 1
fi

echo ""
echo "✅ Prerequisites check complete!"
echo ""
echo "To test Standard GUI:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "To test Real-Time GUI:"
echo "   streamlit run streamlit_app_realtime.py"
echo ""
