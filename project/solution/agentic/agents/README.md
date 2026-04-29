
# Agent Implementations

This directory contains the **core agents** that make up the Agentic Customer Support workflow.
Each agent has a clearly defined, single responsibility and communicates state through
LangGraph-managed state objects.

The agents collectively implement **intent routing, tool invocation, decision‑making,
escalation logic, and memory persistence**.

---

## 🧠 Agent Overview

| Agent | Responsibility |
|------|---------------|
| `intent_agent.py` | Classifies the incoming ticket and decides the routing path |
| `retrieval_agent.py` | Retrieves relevant knowledge and invokes DB-backed tools |
| `analysis_agent.py` | Synthesizes responses, scores confidence, decides escalation |
| `memory_agent.py` | Persists final state and enables inspectable session memory |

Each agent:
- receives a shared LangGraph state dictionary
- may read and/or mutate state
- explicitly returns updated state for downstream agents

---

## 🔀 `intent_agent.py`

### Purpose
- Determine **user intent** from natural-language input
- Consider **ticket metadata** such as urgency or complexity
- Decide the next routing step in the workflow

### Key Outputs
- `intent`: e.g. `qa`, `account_action`, `urgent`, `unknown`
- `next_step`: `knowledge_path`, `account_path`, or `escalation_path`

### Notes
- This agent **does not call tools**
- It must **pass through core state fields** (`user_input`, `ticket_metadata`, `ticket_id`)
  so downstream agents can operate correctly

---

## 📚 `retrieval_agent.py`

### Purpose
- Retrieve relevant knowledge base articles
- Invoke **DB-backed support tools** where applicable

### Tools Used
- Knowledge retrieval (articles / FAQs)
- Account lookup (email → user + subscription)

### Key Outputs
- `retrieved_kb`: structured knowledge results
- `account_info` (when applicable)
- `tools_used`: for auditability

### Notes
- This agent is responsible for **all external data lookups**
- No response synthesis or escalation happens here

---

## 🧠 `analysis_agent.py`

### Purpose
- Combine user input, retrieved knowledge, tool outputs, and memory
- Generate a customer‑facing response
- Compute **confidence score**
- Decide whether to escalate

### Key Logic
- Confidence‑based decisioning
- Metadata‑aware escalation (e.g. high‑urgency tickets)
- Account-actions are treated as sensitive operations

### Outputs Written to State
- `final_answer`
- `confidence`
- `escalated`
- `escalation_reason`

### Notes
- Loads **prior conversation history** from persistent memory
- Writes structured logs for auditability
- Always returns a fully populated state

---

## 💾 `memory_agent.py`

### Purpose
- Persist conversation outcomes and ensure **state is checkpointed**
- Enable **session memory inspection by `thread_id`**
- Make long‑term memory usable across sessions

### Responsibilities
- Explicitly **mutate workflow state** so LangGraph checkpoints record writes
- Append execution metadata (e.g. `actions_taken`)
- Support inspectable state via `get_state_history()`

### Notes
- This agent is essential for satisfying:
  - short‑term (session) memory
  - inspectable workflow state
  - long‑term history persistence

---

## ✅ Memory & State Guarantees

- All agents pass state forward explicitly
- LangGraph checkpointer is enabled at workflow compile time
- State is inspectable by `thread_id`
- Long‑term memory is persisted via SQLite (`ticket_messages`)

---

## 🔍 Debugging & Inspection

To inspect session state:

```python
snapshots = list(
    app.get_state_history(
        config={"configurable": {"thread_id": "TICKET-001"}}
    )
)
snapshots
