#!/bin/bash
# Test script for ANS (Agent Name Server)

set -e

ANS_URL="http://localhost:8001"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 ANS Test Script"
echo "=================="
echo ""

# Check if ANS server is running
echo "📡 Checking if ANS server is running..."
if curl -s "$ANS_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ANS server is running${NC}"
else
    echo -e "${RED}❌ ANS server is NOT running!${NC}"
    echo ""
    echo "Start ANS server with:"
    echo "  uvicorn src.ans.main:app --port 8001"
    echo ""
    exit 1
fi

echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s "$ANS_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "   Response: $HEALTH"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

echo ""

# Test 2: List manifests (empty initially)
echo "2️⃣ Testing list manifests endpoint..."
LIST=$(curl -s "$ANS_URL/api/v1/manifests/list")
if echo "$LIST" | grep -q "\[\]"; then
    echo -e "${GREEN}✅ List manifests (empty)${NC}"
else
    echo -e "${YELLOW}⚠️  List manifests returned: $LIST${NC}"
fi

echo ""

# Test 3: Run Python demo
echo "3️⃣ Running Python demo script..."
if python examples/ans_demo.py; then
    echo -e "${GREEN}✅ Demo script completed${NC}"
else
    echo -e "${RED}❌ Demo script failed${NC}"
    exit 1
fi

echo ""

# Test 4: Run pytest tests
echo "4️⃣ Running pytest tests..."
if pytest tests/test_ans.py -v; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All ANS tests completed successfully!${NC}"

