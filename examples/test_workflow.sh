#!/bin/bash

# Test Workflow Completo per Open Floor Protocol
# Questo script testa un workflow completo multi-agente

set -e

BASE_URL="http://localhost:8000/api/v1"
CONV_ID="conv_workflow_$(date +%s)"

echo "=========================================="
echo "Open Floor Protocol - Test Workflow"
echo "=========================================="
echo ""

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Health Check${NC}"
curl -s http://localhost:8000/health | jq .
echo ""

echo -e "${BLUE}Step 2: Registrazione Agenti${NC}"

echo "Registrazione Agent 1 (Text Generation)..."
curl -s -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_text",
    "agent_name": "Text Generation Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001",
    "conversationalName": "TextBot"
  }' | jq -r '.speakerUri // "ERROR"'
echo ""

echo "Registrazione Agent 2 (Image Generation)..."
curl -s -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_image",
    "agent_name": "Image Generation Agent",
    "capabilities": ["image_generation"],
    "serviceUrl": "http://localhost:8002",
    "conversationalName": "ImageBot"
  }' | jq -r '.speakerUri // "ERROR"'
echo ""

echo "Registrazione Agent 3 (Data Analysis)..."
curl -s -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_data",
    "agent_name": "Data Analysis Agent",
    "capabilities": ["data_analysis"],
    "serviceUrl": "http://localhost:8003",
    "conversationalName": "DataBot"
  }' | jq -r '.speakerUri // "ERROR"'
echo ""

echo -e "${BLUE}Step 3: Lista Agenti Registrati${NC}"
curl -s $BASE_URL/agents/ | jq '.[] | {speakerUri, agent_name, capabilities}'
echo ""

echo -e "${BLUE}Step 4: Discovery per Capability${NC}"
echo "Cercando agenti con capability 'text_generation'..."
curl -s $BASE_URL/agents/capability/text_generation | jq '.[] | {speakerUri, agent_name}'
echo ""

echo -e "${BLUE}Step 5: Floor Control - Richiesta Floor${NC}"
echo "Agent 1 richiede floor..."
RESPONSE=$(curl -s -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_text\",
    \"priority\": 5
  }")
echo $RESPONSE | jq .
GRANTED=$(echo $RESPONSE | jq -r '.granted')
echo ""

if [ "$GRANTED" = "true" ]; then
  echo -e "${GREEN}✓ Floor concesso ad Agent 1${NC}"
else
  echo -e "${YELLOW}⚠ Floor non concesso immediatamente${NC}"
fi
echo ""

echo "Agent 2 richiede floor (sarà in coda)..."
curl -s -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_image\",
    \"priority\": 3
  }" | jq .
echo ""

echo "Agent 3 richiede floor (sarà in coda)..."
curl -s -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_data\",
    \"priority\": 4
  }" | jq .
echo ""

echo -e "${BLUE}Step 6: Verifica Floor Holder${NC}"
HOLDER=$(curl -s $BASE_URL/floor/holder/$CONV_ID | jq -r '.holder')
echo "Current floor holder: $HOLDER"
echo ""

echo -e "${BLUE}Step 7: Invio Utterance${NC}"
echo "Agent 1 invia utterance ad Agent 2..."
curl -s -X POST $BASE_URL/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"sender_speakerUri\": \"tag:test.com,2025:agent_text\",
    \"target_speakerUri\": \"tag:test.com,2025:agent_image\",
    \"text\": \"Can you generate an image of a sunset?\"
  }" | jq '.success'
echo ""

echo -e "${BLUE}Step 8: Release Floor${NC}"
echo "Agent 1 rilascia floor..."
curl -s -X POST $BASE_URL/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_text\"
  }" | jq .
echo ""

echo -e "${BLUE}Step 9: Verifica Nuovo Floor Holder${NC}"
NEW_HOLDER=$(curl -s $BASE_URL/floor/holder/$CONV_ID | jq -r '.holder')
echo "New floor holder: $NEW_HOLDER"
echo ""

echo -e "${BLUE}Step 10: Heartbeat Update${NC}"
echo "Agent 1 aggiorna heartbeat..."
curl -s -X POST $BASE_URL/agents/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_text"
  }' | jq .
echo ""

echo -e "${GREEN}=========================================="
echo "Test Workflow Completato!"
echo "==========================================${NC}"
echo ""
echo "Conversation ID: $CONV_ID"
echo "Puoi continuare a testare con questo conversation_id"
echo ""
echo "Comandi utili:"
echo "  - Lista agenti: curl $BASE_URL/agents/ | jq"
echo "  - Floor holder: curl $BASE_URL/floor/holder/$CONV_ID | jq"
echo "  - Swagger UI: http://localhost:8000/docs"

