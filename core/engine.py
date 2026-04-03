"""
LangGraph state machine for the GUARDIAN-AGENT ReAct loop.
Manages the transition between Reasoning, Acting, and Observing.
"""
import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List, Union
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv(override=True)

# Define the state object
class AgentState(TypedDict):
    query: str
    session_id: str
    thought_history: List[str]
    action: Union[str, None]
    action_input: Union[str, None]
    action_history: List[str]
    observation: Union[str, None]
    final_answer: Union[str, None]
    step_count: int

# Initialize the LLM
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Define the graph
def create_agent_graph():
    from core.nodes import reason_node, action_node, observe_node
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("reason", reason_node)
    workflow.add_node("act", action_node)
    workflow.add_node("observe", observe_node)
    
    # Set entry point
    workflow.set_entry_point("reason")
    
    # Define edges
    workflow.add_edge("act", "observe")
    workflow.add_edge("observe", "reason")
    
    # Conditional edge for final answer vs next action
    def should_continue(state: AgentState):
        if state.get("final_answer") or "Final Answer:" in str(state.get("thought_history", [""])[-1]):
            return "end"
        return "continue"
    
    workflow.add_conditional_edges(
        "reason",
        should_continue,
        {
            "continue": "act",
            "end": END
        }
    )
    
    return workflow.compile()

# Increase recursion limit globally if needed
agent_app = create_agent_graph()
# Note: Recursion limit is set during .invoke() or .stream() usually, 
# but we can set a default in the compile or just handle it in main.py.
