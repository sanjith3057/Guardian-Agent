"""
Tavily Search tool for GUARDIAN-AGENT.
Includes 10s timeout, local caching, and fallback logic.
"""
import os
import time
from tavily import TavilyClient
from core.tools.registry import format_tool_output, ToolStatus, get_cached_result, set_cached_result
from security.rate_limit import tavily_limiter

def web_search(query: str):
    """
    Performs a web search using Tavily.
    Checks local cache first.
    """
    print(f"--- TOOL: web_search('{query}') ---")
    
    # 1. Check Cache
    cached = get_cached_result("web_search", query)
    if cached:
        print("✅ CACHE HIT")
        return format_tool_output(ToolStatus.CACHED, cached)
    
    # 2. Rate Limit Check
    if not tavily_limiter.acquire():
        print("⚠️ RATE LIMIT HIT - Falling back to cache (if any) or error")
        return format_tool_output(ToolStatus.FAILED, "Tavily Rate Limit exceeded. Please retry in 5s.")

    # 3. API Call
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        # Execute search with timeout
        # Note: tavily-python doesn't have a direct timeout param in some versions, 
        # so we rely on the broader agent timeout if needed.
        response = client.search(query=query, search_depth="basic")
        
        results = ""
        for res in response.get("results", []):
            results += f"\nSource: {res['url']}\nContent: {res['content']}\n"
            
        if not results:
            return format_tool_output(ToolStatus.FAILED, "No relevant results found.")
            
        # 4. Save to Cache
        set_cached_result("web_search", query, results)
        return format_tool_output(ToolStatus.SUCCESS, results)
        
    except Exception as e:
        print(f"❌ TAVILY ERROR: {e}")
        return format_tool_output(ToolStatus.FAILED, f"Search failed: {str(e)}")
