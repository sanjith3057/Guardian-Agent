"""
Decision, Action, and Observation nodes for the GUARDIAN-AGENT ReAct loop.
"""
import os
from langchain_core.messages import HumanMessage, SystemMessage
from core.engine import AgentState, llm
from core.tools.search import web_search
from core.tools.math import calculator
from core.tools.python import execute_python
from core.tools.registry import ToolStatus
from obs.tracer import Tracer
import hashlib

# Layer 4: Budget & Loop Guard Constants
MAX_STEPS = 15
LOOP_LIMIT = 2

SYSTEM_PROMPT = """
You are GUARDIAN-AGENT, a security-first ReAct agent.
Follow this format:
Thought: [Your reasoning about what to do next]
Action: [The tool to use: web_search, execute_python, calculator. Must just be the tool name]
Action Input: [The exact input for the tool]

If you have the final answer, or if you can answer without tools, use this format exclusively:
Thought: [Your reasoning]
Final Answer: [Your comprehensive answer]

Current Tools:
- web_search(query): Search the web.
- execute_python(code): Execute Python code (Requires HITL approval).
- calculator(expr): Evaluate math expressions.

Rules:
1. Only one action at a time. Do not write tool arguments in the Action field.
2. If tool results are irrelevant, try another strategy.
3. If you do not need tools, immediately output Final Answer.
"""

def reason_node(state: AgentState):
    """ decides the next step based on the current state. """
    print(f"--- REASONING (Step {state['step_count'] + 1}) ---")
    tracer = Tracer(state.get("session_id", "default_session"))
    
    # Layer 4: Budget Guard
    if state["step_count"] >= MAX_STEPS:
        print("🚨 BUDGET GUARD: Max steps reached. Forcing termination.")
        new_state = state.copy()
        new_state["final_answer"] = "CRITICAL: Agent terminated due to step limit (Budget Guard)."
        return new_state

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"User Query: {state['query']}\nHistory: {state['thought_history']}\nLast Observation: {state['observation']}")
    ]
    
    response = llm.invoke(messages)
    content = response.content
    
    # Simple parser for Thought/Action/Final Answer
    new_state = state.copy()
    new_state["thought_history"].append(content)
    new_state["step_count"] += 1
    
    # LOG TO TRACER
    tracer.log("REASON", content, new_state["step_count"])
    
    if "Final Answer:" in content:
        new_state["final_answer"] = content.split("Final Answer:")[1].strip()
        new_state["action"] = None
    elif "Action:" in content:
        action_parts = content.split("Action:")[1].split("\n")
        # Extract just the alphabetic tool name to avoid trailing args or spaces
        raw_action = action_parts[0].strip().split("(")[0].strip()
        
        if raw_action.lower() == "none" or not raw_action:
            new_state["action"] = None
            new_state["observation"] = "SYSTEM: You output Action: None. You must choose a tool or provide a Final Answer."
        else:
            new_state["action"] = raw_action
            if "Action Input:" in content:
                input_parts = content.split("Action Input:")[1].split("\n")
                new_state["action_input"] = input_parts[0].strip()
            else:
                new_state["action_input"] = ""
    else:
        # Fallback if neither found but still reasoning
        new_state["action"] = None
        new_state["observation"] = "SYSTEM: Parsing error. Ensure you use the exact format requested with either Action/Action Input OR Final Answer."
            
    return new_state

def action_node(state: AgentState):
    """ Executes the chosen action (Tools). """
    action = state.get("action")
    action_input = state.get("action_input")
    
    if not action:
        return state
        
    print(f"--- ACTING: {action}({action_input}) ---")
    tracer = Tracer(state.get("session_id", "default_session"))
    tracer.log("ACTION", f"{action}({action_input})", state["step_count"])
    
    result = {"status": "FAILED", "content": "Unknown tool"}
    
    if action == "web_search":
        result = web_search(action_input)
    elif action == "calculator":
        result = calculator(action_input)
    elif action == "execute_python":
        result = execute_python(action_input)
        
    new_state = state.copy()
    new_state["observation"] = f"STATUS: {result['status']} | CONTENT: {result['content']}"
    
    # Layer 4: Action Fingerprinting & Loop Detection
    action_str = f"{action}({action_input})"
    fingerprint = hashlib.md5(action_str.encode()).hexdigest()
    
    if "action_history" not in new_state:
        new_state["action_history"] = []
    
    new_state["action_history"].append(fingerprint)
    
    # Check for identical repeated failures
    if len(new_state["action_history"]) >= LOOP_LIMIT:
        if new_state["action_history"][-1] == new_state["action_history"][-2] and result["status"] == "FAILED":
            print(f"🚨 LOOP DETECTED: Action {action} failed twice with same input. Self-healing...")
            new_state["observation"] += "\n⚠️ SYSTEM: Loop detected. Please try a different tool or strategy."
            
    return new_state

def observe_node(state: AgentState):
    """ Captures the result of the action. """
    print(f"--- OBSERVING ---")
    tracer = Tracer(state.get("session_id", "default_session"))
    tracer.log("OBSERVATION", state["observation"], state["step_count"])
    return state
