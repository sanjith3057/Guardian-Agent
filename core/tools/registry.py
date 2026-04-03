"""
Tool registry and standardization logic for GUARDIAN-AGENT.
Includes local caching to save Tavily credits.
"""
import os
import json
from enum import Enum
from typing import Dict, Any

class ToolStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FALLBACK = "FALLBACK"
    CACHED = "CACHED"

CACHE_FILE = "cache.json"

def load_cache() -> Dict[str, Any]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: Dict[str, Any]):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached_result(tool_name: str, query: str):
    cache = load_cache()
    key = f"{tool_name}:{query}"
    return cache.get(key)

def set_cached_result(tool_name: str, query: str, result: str):
    cache = load_cache()
    key = f"{tool_name}:{query}"
    cache[key] = result
    save_cache(cache)

def format_tool_output(status: ToolStatus, content: str):
    return {"status": status.value, "content": content}
