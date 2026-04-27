
# Agents

This folder contains all **agent implementations** used in the Agentic AI system.

Each agent is designed to have a **single, well‑defined responsibility**, following separation‑of‑concerns and agentic design principles.

Agents are orchestrated explicitly via a custom LangGraph workflow defined in `agentic/workflow.py`.

---

## Agent Summary

| Agent | File | Responsibility |
|-----|-----|----------------|
| Intent Agent | `intent_agent.py` | Classify user intent and route workflow |
| Retrieval Agent | `retrieval_agent.py` | Retrieve relevant contextual information |
| Analysis Agent | `analysis_agent.py` | Reason over retrieved context and form answers |
| Memory Agent | `memory_agent.py` | Maintain conversational memory and summaries |

---

## Intent Agent
**Purpose:**  
Determine what the user is trying to accomplish (QA, summarization, action, or unknown).

**Key Characteristics:**
- Uses lightweight LLM reasoning
- Does not perform retrieval
- Controls initial workflow routing

---

## Retrieval Agent
**Purpose:**  
Fetch relevant data or documents needed to answer the user's query.

**Key Characteristics:**
- Delegates retrieval logic to tools
- Abstracts data access from reasoning logic
- Prepares structured context for downstream agents

---

## Analysis Agent
**Purpose:**  
Generate a final, user‑facing response.

**Key Characteristics:**
- Combines user input with retrieved context
- Performs reasoning and synthesis
- Produces the `final_answer` field used by the UI

---

## Memory Agent
**Purpose:**  
Preserve conversational continuity across turns.

**Key Characteristics:**
- Summarizes interactions
- Uses LangGraph checkpointer for session memory
- Enables follow‑up questions within the same thread

---

## Design Principles
- One responsibility per agent
- Minimal shared state
- Explicit state updates
- Easy extensibility for future agents

---

## Notes
Agents do **not** directly invoke other agents. All coordination is handled by the workflow orchestrator.
