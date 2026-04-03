"""
Security validator for GUARDIAN-AGENT.
Verifies API keys, budget limits, and environment configuration.
"""
import os
import sys
from dotenv import load_dotenv

def validate_environment():
    """
    Validates that all required environment variables are set and credit limits are sane.
    """
    load_dotenv(override=True)
    
    required_keys = ["GROQ_API_KEY", "TAVILY_API_KEY", "CHROMA_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"❌ CRITICAL ERROR: Missing API keys: {', '.join(missing_keys)}")
        print("Please check your .env file.")
        sys.exit(1)
        
    # Budget check
    try:
        max_steps = int(os.getenv("MAX_STEPS", 10))
        max_tokens = int(os.getenv("MAX_TOKENS", 3000))
        if max_steps > 20 or max_tokens > 10000:
            print("⚠️ WARNING: High budget limits detected. Risk of cost surge.")
    except ValueError:
        print("⚠️ WARNING: Invalid budget limit format in .env. Using defaults.")

    print("✅ Layer 0: Environment validation successful.")
    return True

if __name__ == "__main__":
    validate_environment()
