# 🛡️ GUARDIAN-AGENT

**The Self-Healing ReAct Agent with Deep Observability & Production-Grade Security.**

57% of AI agents fail silently in production. **GUARDIAN-AGENT** is built to be the exception. It doesn't just "reason"; it observes, recovers, and protects itself (and your budget) from common failures like loops, rate limits, and "vibe coding" errors.

---

## 🚀 Key Features (The 5-Layer Stack)

- **Layer 0: Security & Guardrails**: Rate limiting (Token-bucket), secret validation, and log scrubbing.
- **Layer 1: ReAct Core**: State-driven Reasoning loop using **LangGraph**.
- **Layer 2: Secure Tools**: Web Search (Tavily), Sandboxed Python, and Math—all with triple-layer fallbacks.
- **Layer 3: Step-Level Observability**: Real-time Streamlit dashboard tracing every decision and token.
- **Layer 4: Self-Healing**: Automatic strategy pivoting and budget hard-stops (Step/Token limits).

---

## 🛠️ Core Agent Skills (Tools)

1.  **🔍 Deep Web Search**: Powered by **Tavily**. Optimized with 10s timeouts and "Search-to-Cache" fallbacks.
2.  **🐍 Sandboxed Python**: Real-time code execution for complex logic. Protected by **Human-In-The-Loop (HITL)** approval to prevent unintended actions.
3.  **🧮 Enhanced Calculator**: Handles complex math. Falls back to LLM-reasoning if the expression is too abstract for raw evaluation.

---

## 🛡️ Security Pillars

| Pillar | Objective |
| :--- | :--- |
| **Vibe Coding Protection** | HITL approval before any code execution. |
| **Budget Guard** | Hard-stop at $0.05 / 3000 tokens to prevent runaway costs. |
| **PII/Key Scrubber** | Automatic regex-based cleaning of logs and traces. |
| **Rate Limit Resilience** | Exponential backoff for Groq & Tavily API calls. |

---

## 📅 4-Hour Implementation Workflow

*   **0:00–0:30 — Setup**: `pip` installs, `.env` config, and test plan definition.
*   **0:30–1:15 — Layer 1 (Core)**: LangGraph state machine & ReAct loop implementation.
*   **1:15–1:45 — Layer 2 (Tools)**: Building the tool registry with `SUCCESS/FAILED` status feedback.
*   **1:45–2:15 — Layer 3 (Obs)**: TraceEvent dataclasses and Streamlit live viewer.
*   **2:15–2:45 — Layer 4 (Healing)**: Fingerprinting actions and loop detection logic.
*   **2:45–3:30 — Deployment**: Running `failure_injection_demo()` and finalizing documentation.

---

## 🚥 Quick Start

1. **Clone & Install**:
   ```bash
   pip install langgraph langchain-groq tavily-python streamlit python-dotenv
   ```
2. **Configure Security**:
   Create a `.env` file:
   ```env
   GROQ_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   ```
3. **Run Dashboard**:
   ```bash
   streamlit run app.py
   ```

---

*“I'm not waiting for a job to build production-grade AI. I'm shipping it.”*
