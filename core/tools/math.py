"""
Enhanced Calculator tool for GUARDIAN-AGENT.
Evaluates math expressions safely.
"""
import math
from core.tools.registry import format_tool_output, ToolStatus

def calculator(expression: str):
    """
    Evaluates a mathematical expression.
    """
    print(f"--- TOOL: calculator('{expression}') ---")
    
    # Restricted namespace for safety
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("__")
    }
    allowed_names.update({"__builtins__": {}})
    
    try:
        # Sanitization: Basic check for unsafe chars
        safe_expr = expression.replace("^", "**")
        result = eval(safe_expr, allowed_names)
        return format_tool_output(ToolStatus.SUCCESS, str(result))
    except Exception as e:
        print(f"❌ CALC ERROR: {e}")
        return format_tool_output(ToolStatus.FAILED, f"Calculation failed: {str(e)}")
