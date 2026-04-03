"""
Privacy filter and log scrubber for GUARDIAN-AGENT.
Removes sensitive patterns (keys, secrets) from traces.
"""
import re

# Regex for common API key formats (Groq, Tavily, Chroma)
SENSITIVE_PATTERNS = [
    r'gsk_[a-zA-Z0-9]{40,}',
    r'tvly-[a-zA-Z0-9-]{40,}',
    r'ck-[a-zA-Z0-9]{40,}',
    r'[a-zA-Z0-9]{32,}' # Generic long hash
]

def scrub_text(text: str) -> str:
    """
    Scrubs sensitive patterns from the input text.
    """
    if not isinstance(text, str):
        return text
        
    scrubbed = text
    for pattern in SENSITIVE_PATTERNS:
        scrubbed = re.sub(pattern, "[REDACTED]", scrubbed)
    return scrubbed

# Test the scrubber
if __name__ == "__main__":
    test_str = "My keys: gsk_1234567890abcdef1234567890abcdef12345678 and tvly-1234-5678-9012-3456-7890-1234-5678-9012"
    print(f"Original: {test_str}")
    print(f"Scrubbed: {scrub_text(test_str)}")
