#!/usr/bin/env python3
"""
Streamlit GUI for Floor Manager - Interactive Multi-Agent Chat

Run: streamlit run streamlit_app.py
"""

import streamlit as st
import asyncio
import httpx
import os
from datetime import datetime

# Configuration
FLOOR_API = "http://localhost:8000/api/v1"
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
    page_title="OFP Floor Manager Demo",
    page_icon="🎤",
    layout="wide"
)

# Title
st.title("🎤 Open Floor Protocol - Multi-Agent Chat")
st.markdown("**Interactive demo with real AI agents and floor control**")

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
    
    st.header("🎯 Floor Status")
    
    # Get current floor holder
    try:
        response = httpx.get(f"{FLOOR_API}/floor/holder/{CONVERSATION_ID}", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            holder = data.get("holder")  # Can be None
            
            # Find agent name from speakerUri
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
        else:
            st.warning(f"⚠️ API returned status {response.status_code}")
    except Exception as e:
        st.error("🔌 Floor Manager not running")
        st.caption(f"❌ Error: {str(e)}")
        st.caption(f"🔍 Error type: {type(e).__name__}")
        st.caption(f"📡 Trying to connect to: {FLOOR_API}/floor/holder/{CONVERSATION_ID}")
        st.caption("Start with: `docker-compose up`")
        
        # Detailed debug info in expander
        with st.expander("🐛 Full Debug Info"):
            import traceback
            st.code(traceback.format_exc())
            st.write("**Configuration:**")
            st.code(f"FLOOR_API = {FLOOR_API}")
            st.code(f"CONVERSATION_ID = {CONVERSATION_ID}")

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

# User input area
if st.session_state.user_mode == "participant":
    # Select agent to use
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
        
        # Add user message to chat
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
                        # Call LLM
                        with st.spinner(f"{agent_info['emoji']} {selected_agent} thinking..."):
                            # Import LLM agent
                            import sys
                            sys.path.insert(0, os.path.dirname(__file__))
                            from src.agents.llm_agent import LLMAgent
                            
                            # Create agent
                            agent = LLMAgent(
                                speakerUri=agent_info["speakerUri"],
                                agent_name=selected_agent,
                                llm_provider="openai",
                                model_name="gpt-4o-mini",
                                system_prompt=agent_info["system_prompt"]
                            )
                            
                            # Get AI response (sync call)
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
                            
                            # Add AI response to chat
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
        
        # Rerun to show new messages
        st.rerun()
    
    elif user_input and not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar")

else:
    # Observer mode
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
    
    # Auto-run demo button
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
    if st.button("🔄 Refresh Floor Status"):
        st.rerun()

with col3:
    st.caption(f"Conversation ID: `{CONVERSATION_ID}`")

# Instructions
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### Getting Started
    
    1. **Start Floor Manager**:
       ```bash
       docker-compose up
       ```
    
    2. **Enter OpenAI API Key** in the sidebar (required for AI responses)
    
    3. **Choose Your Mode**:
       - **Observer**: Watch agents communicate automatically
       - **Participant**: Chat with AI agents yourself
    
    ### Participant Mode
    
    1. Select an agent to speak as (Budget Analyst, Travel Agent, Coordinator)
    2. Type your message
    3. The agent will:
       - Request floor from Floor Manager
       - Get AI response from GPT-4o-mini
       - Release floor when done
    4. Higher priority agents get floor first!
    
    ### Floor Priority
    
    - 💰 Budget Analyst: Priority 5 (lowest)
    - ✈️ Travel Agent: Priority 7 (medium)
    - 👔 Coordinator: Priority 10 (highest)
    
    ### Features
    
    - ✅ Real-time floor status
    - ✅ Priority-based turn-taking
    - ✅ OpenAI GPT-4o-mini integration
    - ✅ OFP 1.1 compliant
    """)

# Debug info (collapsible)
with st.expander("🔧 Debug Info"):
    st.json({
        "floor_api": FLOOR_API,
        "conversation_id": CONVERSATION_ID,
        "mode": st.session_state.user_mode,
        "message_count": len(st.session_state.messages),
        "api_key_set": bool(api_key)
    })

