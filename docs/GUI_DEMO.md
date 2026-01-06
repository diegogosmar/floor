# 🎨 GUI Demo - Interactive Floor Manager

## Overview

This GUI demo provides a user-friendly web interface to interact with the Open Floor Protocol (OFP) 1.0.1 Floor Manager. Users can chat with AI agents, observe floor control in action, and see priority-based turn-taking in real-time.

## Features

- 💬 **Real-time Chat Interface** - Interactive chat with AI agents
- 🎤 **Floor Status Display** - Visual indicator of who currently has the floor
- 👥 **Multiple AI Agents** - Budget Analyst, Travel Agent, and Coordinator
- 🤖 **AI-Powered Responses** - Uses OpenAI GPT-4o-mini for intelligent responses
- 🎯 **Priority Queue Visualization** - See how floor control prioritizes agents
- 📊 **Two Modes** - Observer mode (watch automated demo) or Participant mode (interact directly)
- 🔄 **Auto-Refresh** - Floor status updates automatically

## Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **OpenAI API Key** (get one at https://platform.openai.com/api-keys)
3. **Floor Manager running** (via Docker Compose)

### Installation

```bash
# Install dependencies (including Streamlit)
pip install -r requirements.txt
```

### Running the Demo

#### Step 1: Start Floor Manager

```bash
# Terminal 1: Start the Floor Manager backend
docker-compose up
```

Wait for: `Application startup complete` message

#### Step 2: Launch GUI

```bash
# Terminal 2: Start the Streamlit GUI
streamlit run streamlit_app.py
```

The GUI will automatically open in your browser at `http://localhost:8501`

#### Step 3: Configure

1. **Enter OpenAI API Key** in the sidebar
   - Click the sidebar (if collapsed)
   - Paste your OpenAI API key (`sk-...`)
   - The key is stored only for the current session

2. **Select Mode**
   - **Observer**: Watch automated multi-agent conversation
   - **Participant**: Chat directly with AI agents

## Usage Guide

### Observer Mode

Watch a fully automated 3-agent conversation:

1. Select **"Observer"** from the mode dropdown
2. Click **"▶️ Run Automated Demo"** button
3. Watch as agents:
   - Request floor in priority order
   - Generate AI responses
   - Release floor automatically
   - Hand off to the next agent

**Example Flow:**
```
💰 Budget Analyst: "What's a reasonable budget for 5 days in Paris?"
🤖 AI Response: "€1,500-2,500 per person..."

✈️ Travel Agent: "What are must-see attractions?"
🤖 AI Response: "Eiffel Tower, Louvre, Notre-Dame..."

👔 Coordinator: "Create a day-by-day itinerary"
🤖 AI Response: "Day 1: Eiffel Tower... Day 2: Louvre..."
```

### Participant Mode

Chat directly with AI agents:

1. Select **"Participant"** from the mode dropdown
2. Choose an agent to speak as:
   - 💰 **Budget Analyst** (Priority 5 - Lowest)
   - ✈️ **Travel Agent** (Priority 7 - Medium)
   - 👔 **Coordinator** (Priority 10 - Highest)
3. Type your message in the chat input
4. The agent will:
   - Request floor from Floor Manager
   - Generate AI response using GPT-4o-mini
   - Display response in chat
   - Release floor when done

**Floor Control Behavior:**
- If floor is free → Agent gets it immediately
- If floor is occupied → Agent is queued by priority
- Higher priority agents get floor first
- Floor automatically passes to next agent in queue

## Available Agents

| Agent | Priority | Role | Emoji | Use Case |
|-------|----------|------|-------|----------|
| **Coordinator** | 10 (Highest) | Organize & summarize | 👔 | Final decisions, coordination |
| **Travel Agent** | 7 (Medium) | Suggest attractions | ✈️ | Recommendations, planning |
| **Budget Analyst** | 5 (Lowest) | Cost estimates | 💰 | Financial analysis |

## UI Components

### Sidebar

- **⚙️ Configuration**
  - OpenAI API Key input (password-protected)
  
- **🎭 Available Agents**
  - List of all agents with priorities
  
- **🎯 Floor Status**
  - Current floor holder indicator
  - Updates automatically every few seconds

### Main Chat Area

- **💬 Conversation Window**
  - Displays all messages chronologically
  - Shows agent name, avatar, and timestamp
  - Auto-scrolls to latest message

- **Input Controls**
  - Agent selector (Participant mode only)
  - Text input field
  - Send button

- **Action Buttons**
  - 🗑️ Clear Chat
  - 🔄 Refresh Floor Status
  - ℹ️ How to Use (expandable instructions)

## Architecture

```
┌─────────────────────────────────────────┐
│     Streamlit Web UI (Browser)         │
│  - Chat Interface                      │
│  - Floor Status Display                │
│  - User Input                          │
└──────────────┬──────────────────────────┘
               │ HTTP REST API
               ↓
┌─────────────────────────────────────────┐
│     Floor Manager (FastAPI)            │
│  - Floor Control Logic                 │
│  - Priority Queue                      │
│  - Envelope Routing                    │
└──────────────┬──────────────────────────┘
               │ OpenAI API
               ↓
┌─────────────────────────────────────────┐
│     OpenAI GPT-4o-mini                 │
│  - AI Response Generation               │
└─────────────────────────────────────────┘
```

## Configuration

### Change Agent Prompts

Edit `streamlit_app.py`:

```python
AGENTS = {
    "Budget Analyst": {
        "system_prompt": "Your custom prompt here",
        "priority": 5,
        "emoji": "💰"
    }
}
```

### Add More Agents

```python
AGENTS["New Agent"] = {
    "speakerUri": "tag:demo,2025:newagent",
    "system_prompt": "You are a helpful assistant...",
    "priority": 8,
    "emoji": "🎨"
}
```

### Change LLM Model

In `streamlit_app.py`, find the LLMAgent initialization:

```python
agent = LLMAgent(
    model_name="gpt-4o-mini"  # Change to "gpt-4o" for better quality
)
```

### Change Floor Manager URL

If Floor Manager runs on a different port or host:

```python
FLOOR_API = "http://your-host:port/api/v1"
```

## Troubleshooting

### GUI Won't Start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
pip install streamlit
```

### Floor Manager Not Found

**Error**: `🔌 Floor Manager not running`

**Solution**:
1. Check if Docker Compose is running: `docker-compose ps`
2. Verify Floor Manager is accessible: `curl http://localhost:8000/health`
3. Check firewall/network settings

### API Key Not Working

**Error**: `OpenAI API error` or `Invalid API key`

**Solution**:
1. Verify API key is correct (starts with `sk-`)
2. Check API key has credits: https://platform.openai.com/usage
3. Ensure API key has access to GPT-4o-mini model

### Agents Not Getting Floor

**Symptom**: Messages show "⏳ Agent queued"

**Solution**:
- This is normal! Another agent has the floor
- Wait for current agent to release floor
- Or manually release floor via Floor Manager API

### Chat Not Updating

**Symptom**: Messages don't appear after sending

**Solution**:
- Click "🔄 Refresh Floor Status" button
- Or refresh browser page (F5)
- Check browser console for errors (F12)

## Example Scenarios

### Scenario 1: Plan a Trip

1. **Budget Analyst**: "What's a reasonable budget for 5 days in Paris?"
2. **Travel Agent**: "What are must-see attractions within that budget?"
3. **Coordinator**: "Create a day-by-day itinerary"

### Scenario 2: Business Meeting

1. **Budget Analyst**: "What's the cost estimate for this project?"
2. **Coordinator**: "What's the timeline and resource allocation?"
3. **Travel Agent**: "What locations should we consider?"

### Scenario 3: Floor Priority Demo

1. All 3 agents request floor simultaneously
2. Watch Coordinator (priority 10) get floor first
3. Then Travel Agent (priority 7)
4. Finally Budget Analyst (priority 5)

## Cost Estimation

Each AI response costs approximately:
- **GPT-4o-mini**: ~$0.0001 per message
- **3-agent demo**: ~$0.0003 total
- **10 messages**: ~$0.001

**Very affordable for testing!**

## Security Notes

- ✅ API keys are stored only in browser session (not saved)
- ✅ No API keys are logged or transmitted to third parties
- ✅ Floor Manager runs locally (no external access)
- ⚠️ Don't commit API keys to Git
- ⚠️ Use environment variables for production

## Deployment

### Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set environment variables (OPENAI_API_KEY)
5. Deploy!

**Result**: Public URL like `https://yourapp.streamlit.app`

### Local Network Access

To access from other devices on your network:

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

Then access via: `http://your-ip:8501`

## Advanced Features

### Custom Scenarios

Edit the prompts in `streamlit_app.py`:

```python
prompts = [
    ("Budget Analyst", "Your custom question"),
    ("Travel Agent", "Another question"),
    ("Coordinator", "Final question")
]
```

### Voice Input (Future)

Could integrate Whisper API for voice input:
```python
audio = st.audio_input("Speak...")
transcription = whisper.transcribe(audio)
```

### Export Chat History

Add export functionality:
```python
if st.button("📥 Export Chat"):
    json.dump(st.session_state.messages, open("chat.json", "w"))
```

## Resources

- **Streamlit Documentation**: https://docs.streamlit.io
- **Floor Manager API Docs**: http://localhost:8000/docs (when running)
- **OFP Specification**: https://github.com/open-voice-interoperability/openfloor-docs
- **OpenAI API Docs**: https://platform.openai.com/docs

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
2. Review Floor Manager logs: `docker-compose logs`
3. Check Streamlit logs in terminal
4. Open issue on GitHub

## License

Same license as Floor Manager project (MIT).


