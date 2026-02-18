#!/usr/bin/env python3
"""
Streamlit GUI with Real-Time Updates (SSE)

This version uses Server-Sent Events (SSE) for real-time floor status updates.
Uses JavaScript custom component to connect to FastAPI SSE endpoint.

Run: streamlit run streamlit_app_realtime.py
"""

import streamlit as st
import asyncio
import httpx
import os
from datetime import datetime
import streamlit.components.v1 as components

# Configuration
FLOOR_API = "http://localhost:8787/api/v1"
CONVERSATION_ID = "streamlit_chat_001"

# Available agents
AGENTS = {
    "Budget Analyst": {
        "speakerUri": "tag:demo,2025:budget",
        "system_prompt": "You are a budget analyst. Provide cost estimates and financial advice. Be concise (2-3 sentences).",
        "priority": 5,
        "emoji": "💰"
    },
    "Travel Agent": {
        "speakerUri": "tag:demo,2025:travel",
        "system_prompt": "You are a travel expert. Suggest attractions and itineraries. Be concise (2-3 sentences).",
        "priority": 7,
        "emoji": "✈️"
    },
    "Coordinator": {
        "speakerUri": "tag:demo,2025:coordinator",
        "system_prompt": "You are a project coordinator. Organize and summarize discussions. Be concise (2-3 sentences).",
        "priority": 10,
        "emoji": "👔"
    }
}

# Page config
st.set_page_config(
    page_title="OFP Floor Manager Demo (Real-Time)",
    page_icon="🎤",
    layout="wide"
)

# Title
st.title("🎤 Open Floor Protocol - Multi-Agent Chat")
st.markdown("**Interactive demo with real-time floor status updates** ⚡")

# SSE JavaScript Component
def create_sse_component():
    """Create JavaScript component for SSE connection"""
    sse_js = f"""
    <script>
    (function() {{
        const eventSource = new EventSource('{FLOOR_API}/events/floor/{CONVERSATION_ID}');
        const statusDiv = document.getElementById('floor-status-realtime');
        
        eventSource.onmessage = function(event) {{
            try {{
                const data = JSON.parse(event.data);
                
                if (data.type === 'floor_update' || data.type === 'initial_status') {{
                    // Update status display
                    if (statusDiv) {{
                        const holder = data.data?.holder || data.holder || 'None';
                        const queue = data.data?.queue || data.queue || [];
                        
                        let html = '<div style="padding: 10px; border-radius: 5px; background: #f0f2f6;">';
                        html += '<strong>🎯 Floor Status (Real-Time)</strong><br>';
                        
                        if (holder && holder !== 'None') {{
                            html += '<div style="color: green; margin-top: 5px;">✅ Holder: ' + holder + '</div>';
                        }} else {{
                            html += '<div style="color: gray; margin-top: 5px;">⏸️ Floor is free</div>';
                        }}
                        
                        if (queue && queue.length > 0) {{
                            html += '<div style="margin-top: 5px;">📋 Queue: ' + queue.length + ' waiting</div>';
                        }}
                        
                        html += '</div>';
                        statusDiv.innerHTML = html;
                    }}
                    
                    // Trigger Streamlit rerun by updating a hidden element
                    window.parent.postMessage({{
                        type: 'streamlit:setFrameHeight',
                        height: document.body.scrollHeight
                    }}, '*');
                }}
            }} catch (e) {{
                console.error('SSE parse error:', e);
            }}
        }};
        
        eventSource.onerror = function(error) {{
            console.error('SSE error:', error);
            if (statusDiv) {{
                statusDiv.innerHTML = '<div style="color: red;">🔌 Connection lost</div>';
            }}
        }};
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {{
            eventSource.close();
        }});
    }})();
    </script>
    <div id="floor-status-realtime"></div>
    """
    return sse_js

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # OpenAI API Key
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Required for AI responses"
    )
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.divider()
    
    st.header("🎭 Available Agents")
    for name, info in AGENTS.items():
        st.markdown(f"{info['emoji']} **{name}** (priority: {info['priority']})")
    
    st.divider()
    
    st.header("🎯 Floor Status (Real-Time)")
    
    # SSE Component for real-time updates
    components.html(create_sse_component(), height=150)
    
    # Fallback: Also show current status via HTTP
    try:
        response = httpx.get(f"{FLOOR_API}/floor/holder/{CONVERSATION_ID}", timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            holder = data.get("holder")  # Can be None
            
            holder_name = "None"
            holder_emoji = "⏸️"
            
            # Only search if holder is not None
            if holder:
                for name, info in AGENTS.items():
                    if holder in info["speakerUri"]:
                        holder_name = name
                        holder_emoji = info["emoji"]
                        break
            
            if holder:
                st.success(f"{holder_emoji} **{holder_name}** has floor")
            else:
                st.info("⏸️ Floor is free")
    except:
        st.warning("🔌 Floor Manager not running")
        st.caption("Start with: `docker-compose up`")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_mode" not in st.session_state:
    st.session_state.user_mode = "observer"

# Mode selection
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Conversation")

with col2:
    mode = st.selectbox(
        "Your role",
        ["Observer", "Participant"],
        key="mode_select"
    )
    st.session_state.user_mode = mode.lower()

# Display chat messages
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "🤖")):
            st.markdown(f"**{msg['name']}**")
            st.write(msg["content"])
            if "timestamp" in msg:
                st.caption(msg["timestamp"])

# User input area (same as original)
if st.session_state.user_mode == "participant":
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.chat_input("Type your message...")
    
    with col2:
        selected_agent = st.selectbox(
            "Speak as",
            list(AGENTS.keys()),
            key="agent_select"
        )
    
    if user_input and api_key:
        agent_info = AGENTS[selected_agent]
        
        st.session_state.messages.append({
            "role": "user",
            "name": selected_agent,
            "content": user_input,
            "avatar": agent_info["emoji"],
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Request floor
        with st.spinner(f"{agent_info['emoji']} {selected_agent} requesting floor..."):
            try:
                response = httpx.post(
                    f"{FLOOR_API}/floor/request",
                    json={
                        "conversation_id": CONVERSATION_ID,
                        "speakerUri": agent_info["speakerUri"],
                        "priority": agent_info["priority"]
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    granted = data.get("granted", False)
                    
                    if granted:
                        # Call LLM (same as original)
                        with st.spinner(f"{agent_info['emoji']} {selected_agent} thinking..."):
                            import sys
                            sys.path.insert(0, os.path.dirname(__file__))
                            from src.agents.llm_agent import LLMAgent
                            
                            agent = LLMAgent(
                                speakerUri=agent_info["speakerUri"],
                                agent_name=selected_agent,
                                llm_provider="openai",
                                model_name="gpt-4o-mini",
                                system_prompt=agent_info["system_prompt"]
                            )
                            
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            ai_response = loop.run_until_complete(
                                agent.process_utterance(
                                    CONVERSATION_ID,
                                    user_input,
                                    "tag:user,2025:human"
                                )
                            )
                            loop.close()
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "name": f"{selected_agent} (AI)",
                                "content": ai_response,
                                "avatar": agent_info["emoji"],
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            })
                            
                            # Release floor
                            httpx.post(
                                f"{FLOOR_API}/floor/release",
                                json={
                                    "conversation_id": CONVERSATION_ID,
                                    "speakerUri": agent_info["speakerUri"]
                                },
                                timeout=5.0
                            )
                    else:
                        st.warning(f"⏳ {selected_agent} queued. Another agent has floor.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        st.rerun()
    
    elif user_input and not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar")

else:
    st.info("👁️ **Observer Mode** - Watch agents communicate (set to Participant to join)")
    
    # Custom green button style for primary buttons
    st.markdown("""
    <style>
    button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #218838 !important;
    }
    button[kind="primary"]:focus {
        background-color: #28a745 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("▶️ Run Automated Demo", type="primary"):
        if not api_key:
            st.error("⚠️ Please enter your OpenAI API Key in the sidebar first!")
        else:
            with st.spinner("🤖 Running multi-agent conversation..."):
                try:
                    # Import LLM agent
                    import sys
                    sys.path.insert(0, os.path.dirname(__file__))
                    from src.agents.llm_agent import LLMAgent
                    
                    # Create agents
                    agents_to_run = []
                    for name, info in AGENTS.items():
                        agent = LLMAgent(
                            speakerUri=info["speakerUri"],
                            agent_name=name,
                            llm_provider="openai",
                            model_name="gpt-4o-mini",
                            system_prompt=info["system_prompt"]
                        )
                        agents_to_run.append((name, agent, info))
                    
                    # Scenario prompts
                    prompts = [
                        ("Budget Analyst", "We're planning a 5-day trip to Paris. What's a reasonable budget per person?"),
                        ("Travel Agent", "Based on a mid-range budget, what are the must-see attractions in Paris?"),
                        ("Coordinator", "Great! Let's create a day-by-day itinerary combining budget and top attractions.")
                    ]
                    
                    # Run conversation
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    for agent_name, prompt in prompts:
                        # Find agent info
                        agent_info = AGENTS[agent_name]
                        agent = next(a for n, a, _ in agents_to_run if n == agent_name)
                        
                        # Add user prompt to chat
                        st.session_state.messages.append({
                            "role": "user",
                            "name": f"{agent_name} (Auto)",
                            "content": f"🎬 {prompt}",
                            "avatar": agent_info["emoji"],
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                        
                        # Request floor
                        response = httpx.post(
                            f"{FLOOR_API}/floor/request",
                            json={
                                "conversation_id": CONVERSATION_ID,
                                "speakerUri": agent_info["speakerUri"],
                                "priority": agent_info["priority"]
                            },
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            # Wait for floor if needed
                            max_wait = 10
                            for _ in range(max_wait):
                                holder_resp = httpx.get(
                                    f"{FLOOR_API}/floor/holder/{CONVERSATION_ID}",
                                    timeout=5.0
                                )
                                if holder_resp.status_code == 200:
                                    holder_data = holder_resp.json()
                                    if agent_info["speakerUri"] in holder_data.get("holder", ""):
                                        break
                                import time
                                time.sleep(1)
                            
                            # Get AI response
                            ai_response = loop.run_until_complete(
                                agent.process_utterance(
                                    CONVERSATION_ID,
                                    prompt,
                                    "tag:demo,2025:system"
                                )
                            )
                            
                            # Add AI response to chat
                            st.session_state.messages.append({
                                "role": "assistant",
                                "name": f"{agent_name} (AI)",
                                "content": ai_response,
                                "avatar": agent_info["emoji"],
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            })
                            
                            # Release floor
                            httpx.post(
                                f"{FLOOR_API}/floor/release",
                                json={
                                    "conversation_id": CONVERSATION_ID,
                                    "speakerUri": agent_info["speakerUri"]
                                },
                                timeout=5.0
                            )
                    
                    loop.close()
                    
                    st.success("✅ Automated demo completed!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error running demo: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                
                # Rerun to show messages
                st.rerun()

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

with col3:
    st.caption(f"Conversation ID: `{CONVERSATION_ID}`")

# Instructions
with st.expander("ℹ️ How Real-Time Updates Work"):
    st.markdown("""
    ### Real-Time Floor Status
    
    This version uses **Server-Sent Events (SSE)** for real-time updates:
    
    1. **JavaScript Component**: Connects to FastAPI SSE endpoint
    2. **Event Stream**: Receives floor status updates automatically
    3. **Auto-Update**: Floor status updates without page refresh
    
    ### Technical Details
    
    - **SSE Endpoint**: `GET /api/v1/events/floor/{conversation_id}`
    - **Update Frequency**: Real-time (when floor changes)
    - **Fallback**: HTTP polling if SSE unavailable
    
    ### Requirements
    
    - Floor Manager must have SSE endpoint enabled
    - Browser must support EventSource API (all modern browsers)
    - CORS must allow SSE connections
    """)

