# 🛡️ GUARDIAN-AGENT: The Developer Playbook
*A comprehensive guide and memory export for replicating the 5-Layer Security-First ReAct Architecture in future projects.*

---

## 🛑 The Core Problem
When building AI agents, standard implementations (like basic LangChain/LlamaIndex agents) often suffer from:
1. **"Vibe Coding" Errors:** Agents executing unintended/unsafe code without supervision.
2. **Infinite Loops:** Agents getting stuck in a Reason -> Act -> Fail loop, draining API credits.
3. **Silent Failures:** Lack of visibility into *why* an agent made a decision.
4. **Token/Budget Exhaustion:** API limits being hit (429 errors) resulting in application crashes.

## 🌟 The GUARDIAN Solution Matrix (5 Layers)
To solve these, we structured GUARDIAN-AGENT into 5 distinct, autonomous layers. You can use this exact matrix for any future agentic project.

### Layer 0: Security & Guardrails (The Shield)
- **Token-Bucket Rate Limiter:** Built into `security/rate_limit.py` to ensure you never exceed API limits (e.g., Groq's 30 RPM).
- **Local Fallback Cache:** A local `cache.json` that stores search results to save API credits and latency on duplicate queries.
- **Privacy Scrubber:** Regex-based PII/Secret removal in `security/privacy.py` so API keys never leak into logs.

### Layer 1: ReAct Core Loop (The Brain)
- **State Machine Engine:** Built using **LangGraph** (`core/engine.py`).
- **Nodes & Edges:** Explicit `reason`, `act`, and `observe` nodes that form a continuous cycle until a `final_answer` is reached.

### Layer 2: Secure Tools & Fallbacks (The Hands)
- **Human-In-The-Loop (HITL):** Crucial for execution tools (like Python in `core/tools/python.py`). The agent pauses and asks the human for permission before running code.
- **Triple-Layer Tool Registry:** Every tool returns a standardized dictionary `{"status": "SUCCESS/FAILED", "content": ...}` instead of just crashing on error. 

### Layer 3: Observability (The Eyes)
- **Persistent Tracer:** `obs/tracer.py` writes every thought, action, and token count to a session-specific `.json` file.
- **Modern Dashboard:** Connected the trace file directly to a **Streamlit** front-end (`app.py`), transforming a CLI tool into an interactive UI with live metrics and charts.

### Layer 4: Self-Healing & Loop Guard (The Doctor)
- **Action Fingerprinting:** Hashing actions (e.g., `md5("web_search('Python info')")`) to detect identical retries (`core/nodes.py`).
- **Loop Interception:** If an action fails twice in a row with the exact same input, the agent catches it and forces a pivot.
- **Budget Guard:** A hard stop (e.g., 10 steps) to automatically kill runaway sessions.

---

## 📂 Ideal Project Structure
For your future projects, copy this directory layout to maintain separation of concerns:

```text
my-new-agent/
│
├── core/                  # The Brain & Hands
│   ├── engine.py          # LLM init and LangGraph state machine config
│   ├── nodes.py           # Logic for Reason, Act, and Observe steps
│   ├── memory.py          # Vector DB connections (e.g., Chroma)
│   └── tools/             # Action definitions
│       ├── registry.py    # Base tool interfaces and caching mechanisms
│       ├── search.py      # Tavily/Web interactions
│       └── python.py      # Sandboxed code execution
│
├── security/              # The Shield
│   ├── validator.py       # API key and .env checks
│   ├── rate_limit.py      # TokenBucket implementation
│   └── privacy.py         # Regex scrubber for logs
│
├── obs/                   # The Eyes
│   └── tracer.py          # Custom logging JSON mechanism
│
├── app.py                 # The User Interface (Streamlit Dashboard/Chat)
├── .env                   # Environment variables (NEVER COMMITTED)
└── requirements.txt       # Core dependencies: langgraph, streamlit, etc.
```

---

## 🛠️ Key Technical Takeaways

1. **State is King:** Use `TypedDict` in LangGraph to maintain a strict schema. Track `step_count`, `thought_history`, and `action_history` persistently to give your agent true context.
2. **Never Trust Tools:** Wrap all tool invocations in `try/except` blocks and return `"FAILED"` statuses to the LLM instead of crashing the Python process. The LLM is smart enough to pivot if you tell it that it failed.
3. **Decouple UI from Logic:** Run the agent as an imported module inside of Streamlit, and use Streamlit session states (`st.session_state`) to track interactions without destroying the agent's graph memory.

*Keep this playbook handy whenever you sit down to architect a new AI agent from scratch!*
