# 🎨 GUI Demo - Interactive Floor Manager

## ✨ Features

- 💬 **Real-time Chat Interface** - Chat with AI agents
- 🎤 **Floor Status Display** - See who has the floor
- 👥 **Multiple Agents** - Budget Analyst, Travel Agent, Coordinator
- 🤖 **AI Powered** - GPT-4o-mini for intelligent responses
- 🎯 **Priority Queue** - Visual floor control with priorities
- 📊 **Observer/Participant Modes** - Watch or join conversations

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# Streamlit will be installed automatically
```

### 2. Start Floor Manager

```bash
# Terminal 1
docker-compose up
```

### 3. Launch GUI

```bash
# Terminal 2
streamlit run streamlit_app.py
```

**Opens automatically in browser:** `http://localhost:8501`

---

## 🎯 How to Use

### First Time Setup

1. **Enter OpenAI API Key** in the sidebar
   - Click sidebar (if collapsed)
   - Paste your `sk-...` key
   - Key is stored for the session

2. **Check Floor Status**
   - Sidebar shows current floor holder
   - Updates automatically

### Observer Mode (Watch Demo)

1. Select **"Observer"** in dropdown
2. Click **"Run Automated Demo"** to watch agents talk
3. See floor handoff in real-time

### Participant Mode (Interactive)

1. Select **"Participant"** in dropdown
2. Choose an agent to speak as:
   - 💰 **Budget Analyst** (Priority 5)
   - ✈️ **Travel Agent** (Priority 7)
   - 👔 **Coordinator** (Priority 10)
3. Type your message
4. Agent will:
   - Request floor
   - Get AI response
   - Release floor

---

## 🎭 Available Agents

| Agent | Priority | Role | Emoji |
|-------|----------|------|-------|
| **Coordinator** | 10 (Highest) | Organize & summarize | 👔 |
| **Travel Agent** | 7 (Medium) | Suggest attractions | ✈️ |
| **Budget Analyst** | 5 (Lowest) | Cost estimates | 💰 |

---

## 📊 UI Components

```
┌─────────────────────────────────────────────────┐
│  🎤 Open Floor Protocol - Multi-Agent Chat     │
├─────────────────────────────────────────────────┤
│  Sidebar              │  Main Chat Area         │
│  ┌──────────────┐    │  ┌──────────────────┐  │
│  │ API Key      │    │  │ 💬 Conversation  │  │
│  │ ──────────   │    │  │                  │  │
│  ├──────────────┤    │  │ 💰: "Budget for  │  │
│  │ 🎭 Agents    │    │  │     Paris?"      │  │
│  │              │    │  │                  │  │
│  │ 💰 Budget(5) │    │  │ 🤖: "€1500-2500" │  │
│  │ ✈️  Travel(7)│    │  │                  │  │
│  │ 👔 Coord(10) │    │  └──────────────────┘  │
│  ├──────────────┤    │                        │
│  │ 🎯 Floor     │    │  [Select Agent ▼] ✈️  │
│  │   Status     │    │  [Type message...   ] │
│  │              │    │                        │
│  │ ✅ Coord has │    │  [🗑️] [🔄] [ℹ️]      │
│  │    floor     │    │                        │
│  └──────────────┘    │                        │
└─────────────────────────────────────────────────┘
```

---

## 🎬 Example Scenarios

### Scenario 1: Plan a Trip

1. **You as Budget Analyst**: "What's a reasonable budget for 5 days in Paris?"
2. **AI responds**: "€1,500-2,500 per person for mid-range accommodation..."
3. **You as Travel Agent**: "What are must-see attractions?"
4. **AI responds**: "Eiffel Tower, Louvre, Notre-Dame..."
5. **You as Coordinator**: "Create a day-by-day itinerary"
6. **AI responds**: "Day 1: Eiffel Tower..."

### Scenario 2: Floor Priority Demo

1. All 3 agents request floor at once
2. Coordinator (priority 10) gets it first
3. Travel Agent (priority 7) next
4. Budget Analyst (priority 5) last

---

## 🔧 Advanced Configuration

### Change Agent Prompts

Edit `streamlit_app.py`:

```python
AGENTS = {
    "Budget Analyst": {
        "system_prompt": "Your custom prompt here",
        "priority": 5,
        # ...
    }
}
```

### Add More Agents

```python
AGENTS["New Agent"] = {
    "speakerUri": "tag:demo,2025:newagent",
    "system_prompt": "You are...",
    "priority": 8,
    "emoji": "🎨"
}
```

### Change LLM Model

In `streamlit_app.py`, line ~180:

```python
model_name="gpt-4o-mini"  # Change to "gpt-4o" for better quality
```

---

## 🌐 Opzione 2: Web UI Completa (React + WebSocket)

Per un'interfaccia più professionale:

### Frontend (React)
```bash
npx create-react-app floor-ui
cd floor-ui
npm install socket.io-client
```

### Backend (WebSocket)
```python
# Add to src/main.py
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Real-time updates
```

**Vantaggi**:
- ✅ Real-time bidirectional updates
- ✅ Professional UI
- ✅ Mobile-responsive
- ❌ Più complesso (JavaScript + Python)

---

## 🎨 Opzione 3: Gradio (Ancora Più Semplice)

```python
import gradio as gr

def chat(message, history):
    # Call Floor Manager
    return ai_response

gr.ChatInterface(chat).launch()
```

**Vantaggi**:
- ✅ 10 linee di codice
- ✅ Chat interface predefinita
- ✅ Deploy gratis su Hugging Face Spaces
- ❌ Meno personalizzabile

---

## 📊 Confronto Opzioni

| Feature | Streamlit | React+WS | Gradio |
|---------|-----------|----------|--------|
| **Semplicità** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Personalizzazione** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Real-time** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Deploy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Costo** | Gratis | Gratis/Paid | Gratis |
| **Tempo** | 1 ora | 1 giorno | 30 min |

---

## 🚀 Deploy in Cloud

### Streamlit Cloud (Gratis)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy! ✨

**Result**: `https://yourapp.streamlit.app`

### Railway/Vercel (Per React)

```bash
# Vercel
vercel deploy

# Railway
railway up
```

---

## 🎯 Prossimi Passi

1. **Prova Streamlit Demo** (già pronta!)
2. **Aggiungi features**:
   - Save/load conversations
   - Export chat history
   - Voice input (Whisper API)
   - Agent avatar images
3. **Deploy** su Streamlit Cloud
4. **Condividi** con altri utenti!

---

## 📚 Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Floor Manager API**: http://localhost:8000/docs
- **OFP Specification**: https://github.com/open-voice-interoperability/openfloor-docs

---

## 💡 Tips

- 🔑 **API Key**: Store in environment variable for security
- 🎨 **Customize**: Edit `streamlit_app.py` for your use case
- 🚀 **Performance**: Use `st.cache_data` for expensive operations
- 📊 **Analytics**: Add Streamlit analytics for usage tracking

---

**Ready to try? Run:**
```bash
streamlit run streamlit_app.py
```

🎉 **Enjoy your interactive Floor Manager!**

