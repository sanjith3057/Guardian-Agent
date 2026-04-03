"""
Sandboxed Python executor for GUARDIAN-AGENT.
Requires Human-In-The-Loop (HITL) approval.
"""
import os
import sys
import io
from core.tools.registry import format_tool_output, ToolStatus

def execute_python(code: str):
    """
    Executes Python code and returns the stdout.
    """
    print("\n--- 🛡️ SECURITY CHECK: PYTHON EXECUTION ---")
    print(f"CODE TO EXECUTE:\n{code}")
    print("-------------------------------------------")
    
    # HITL Approval
    confirm = input("⚠️ APPROVE EXECUTION? (y/n): ").strip().lower()
    if confirm != 'y':
        return format_tool_output(ToolStatus.FAILED, "Execution REJECTED by user.")

    print("--- EXECUTING ---")
    
    output = io.StringIO()
    sys.stdout = output
    try:
        # Note: This is an internal simplified sandbox. 
        # In production, this would be a Docker container.
        import json
        import time
        allowed_globals = {
            "__builtins__": __builtins__,
            "os": os,
            "sys": sys,
            "json": json,
            "time": time
        }
        exec(code, allowed_globals, {})
        sys.stdout = sys.__stdout__
        return format_tool_output(ToolStatus.SUCCESS, output.getvalue() or "Code executed with no output.")
    except Exception as e:
        sys.stdout = sys.__stdout__
        return format_tool_output(ToolStatus.FAILED, f"Execution failed: {str(e)}")
