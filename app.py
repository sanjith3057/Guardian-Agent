"""
🛡️ GUARDIAN-AGENT Interactive Interface.
Modern Streamlit chat UI with live observability and metrics.
"""
import streamlit as st
import time
import os
from dotenv import load_dotenv

# Load env variables before importing modules that rely on them
load_dotenv(override=True)
from security.validator import validate_environment
from core.engine import agent_app
import uuid

st.set_page_config(page_title="🛡️ GUARDIAN-AGENT", page_icon="🛡️", layout="wide")

# Ensure environment is valid
if not validate_environment():
    st.error("❌ Environment validation failed. Please check your .env file and API keys.")
    st.stop()

# Initialize session state for chat history and metrics
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_steps" not in st.session_state:
    st.session_state.total_steps = 0
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "session_id" not in st.session_state:
    st.session_state.session_id = f"st_session_{uuid.uuid4().hex[:8]}"
if "tool_usage" not in st.session_state:
    st.session_state.tool_usage = {"web_search": 0, "calculator": 0, "execute_python": 0, "fallback": 0}
if "query_performance" not in st.session_state:
    st.session_state.query_performance = [] # List of dicts {query_num, steps, time_taken, score}

# Sidebar for Metrics & Visuals
with st.sidebar:
    st.title("🛡️ GUARDIAN-AGENT")
    st.caption("Production-Grade Self-Healing ReAct")
    
    st.divider()
    st.subheader("📊 Session Health Score")
    
    # Calculate health based on steps (Max 10 per request usually, let's track totals)
    budget = 50 # Total allowed steps per session (example metric)
    remaining = max(0, budget - st.session_state.total_steps)
    health_pct = int((remaining / budget) * 100)
    
    st.progress(health_pct / 100, text=f"Budget Guard: {health_pct}%")
    
    col1, col2 = st.columns(2)
    col1.metric("Total Steps", st.session_state.total_steps)
    col2.metric("Est. Tokens", "N/A") # Placeholder as we didn't hook token counting yet
    
    st.divider()
    if st.button("Clear History & Cache"):
        st.session_state.messages = []
        st.session_state.total_steps = 0
        st.session_state.tool_usage = {"web_search": 0, "calculator": 0, "execute_python": 0, "fallback": 0}
        st.session_state.query_performance = []
        if os.path.exists("cache.json"):
            os.remove("cache.json")
        st.rerun()

# Layout: Tabs for Chat and Analytics
tab1, tab2 = st.tabs(["💬 Agent Chat", "📊 Analytics Dashboard"])

with tab1:
    st.markdown("### 💬 Agent Interaction")
    chat_container = st.container()

with chat_container:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with tab2:
    st.markdown("### 📊 Performance Analytics")
    st.caption("Live metrics evaluating GUARDIAN-AGENT's reasoning and tool efficiency.")
    
    if len(st.session_state.query_performance) == 0:
        st.info("Ask the agent some questions to generate analytics!")
    else:
        # Top level KPIs
        avg_score = sum(q["Score"] for q in st.session_state.query_performance) / max(1, len(st.session_state.query_performance))
        avg_time = sum(q["Time (s)"] for q in st.session_state.query_performance) / max(1, len(st.session_state.query_performance))
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Average Answer Confidence", f"{avg_score:.1f}/100")
        kpi2.metric("Average Latency", f"{avg_time:.2f}s")
        kpi3.metric("Total Queries Processed", len(st.session_state.query_performance))
        
        st.divider()
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### 🛠️ Tool Invocation Distribution")
            # Filter out unused tools for a cleaner chart
            usage_data = {k: v for k, v in st.session_state.tool_usage.items() if v > 0}
            if usage_data:
                st.bar_chart(usage_data)
            else:
                st.write("No tools used yet.")
                
        with col_chart2:
            st.markdown("#### ⏱️ Efficiency Over Time (Steps per Query)")
            # Create a simple list of steps for the line chart
            steps_data = [q["Steps"] for q in st.session_state.query_performance]
            if steps_data:
                st.line_chart(steps_data)
        
        st.markdown("#### 📜 Query Ledger")
        st.dataframe(st.session_state.query_performance, use_container_width=True)

# Accept user input (Must be at the root level to reliably render at the bottom of the screen)
if prompt := st.chat_input("Ask a question (e.g., 'Compare population of Tokyo and Dubai')"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Render into the chat container inside tab1
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("🧠 Analyzing request...", expanded=True) as status:
                
                initial_state = {
                    "query": prompt,
                    "session_id": st.session_state.session_id,
                    "thought_history": [],
                    "action": None,
                    "action_input": None,
                    "action_history": [],
                    "observation": None,
                    "final_answer": None,
                    "step_count": 0
                }
                
                final_state = None
                start_time = time.time()
                query_steps = 0
                failed_tools = 0
                
                try:
                    for event in agent_app.stream(initial_state, config={"recursion_limit": 50}):
                        if "reason" in event:
                            final_state = event["reason"]
                            if final_state.get("thought_history"):
                                st.write(f"🤔 **Reasoning**: {final_state['thought_history'][-1][:120]}...")
                                st.session_state.total_steps += 1
                                query_steps += 1
                        if "act" in event:
                            action = event['act'].get('action')
                            action_input = event['act'].get('action_input')
                            st.write(f"🛠️ **Action**: `{action}` (`{action_input}`)")
                            if action in st.session_state.tool_usage:
                                st.session_state.tool_usage[action] += 1
                            else:
                                st.session_state.tool_usage["fallback"] += 1
                        if "observe" in event:
                            obs = event['observe'].get('observation', "")
                            st.write(f"👀 **Observation**: {obs[:120]}...")
                            if "FAILED" in obs:
                                failed_tools += 1
                            
                    status.update(label="✅ Request complete!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="❌ Error during execution", state="error", expanded=True)
                    st.error(f"{e}")
                    
            # Calculate query performance metrics
            time_taken = round(time.time() - start_time, 2)
            ans_score = max(0, 100 - (query_steps * 5) - (failed_tools * 10))
            st.session_state.query_performance.append({
                "Query": f"Q{len(st.session_state.query_performance)+1}",
                "Steps": query_steps,
                "Time (s)": time_taken,
                "Score": ans_score
            })
                    
            if final_state:
                if final_state.get("final_answer"):
                    answer = final_state['final_answer']
                else:
                    last_thought = final_state.get("thought_history", [""])[-1]
                    if "Final Answer:" in last_thought:
                        answer = last_thought.split("Final Answer:")[1].strip()
                    else:
                        answer = "*I couldn't formulate a final answer, but check the steps above.*"
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            
    st.rerun()

# End of file
