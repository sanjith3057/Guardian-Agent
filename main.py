"""
Main entry point for interacting with GUARDIAN-AGENT.
"""
import os
import uuid
from security.validator import validate_environment
from core.engine import agent_app

def run_agent():
    print("🛡️ GUARDIAN-AGENT Ready.")
    
    if not validate_environment():
        return

    # Use a persistent session ID for the dashboard
    session_id = "live_session"
    
    # Clean up previous live session trace if it exists
    trace_file = f"trace_{session_id}.json"
    if os.path.exists(trace_file):
        os.remove(trace_file)
    
    while True:
        try:
            query = input("\n👤 User (type 'exit' to quit): ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                break
                
            initial_state = {
                "query": query,
                "session_id": session_id,
                "thought_history": [],
                "action": None,
                "action_input": None,
                "action_history": [],
                "observation": None,
                "final_answer": None,
                "step_count": 0
            }
            
            print(f"\n🚀 Processing your request...")
            
            final_state = None
            # Set a high recursion limit for complex research
            for event in agent_app.stream(initial_state, config={"recursion_limit": 50}):
                if "reason" in event:
                    final_state = event["reason"]
                if "observe" in event:
                    # After an observation, we should check if the next step is reasoning
                    pass

            if final_state and final_state.get("final_answer"):
                print(f"\n🤖 GUARDIAN: {final_state['final_answer']}")
            else:
                # Check thought history for a final answer just in case the node didn't set it
                last_thought = final_state["thought_history"][-1] if final_state and final_state.get("thought_history") else ""
                if "Final Answer:" in last_thought:
                    ans = last_thought.split("Final Answer:")[1].strip()
                    print(f"\n🤖 GUARDIAN: {ans}")
                else:
                    print("\n🤖 GUARDIAN: I couldn't reach a final answer. Please check the dashboard.")
        
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_agent()
