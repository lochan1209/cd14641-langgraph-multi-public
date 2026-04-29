
# Agentic Customer Support System (CultPass)

This repository implements an **agentic, multi‑step customer support system**
built using **LangGraph**, **LangChain**, and **SQLite**.

The goal of the system is to demonstrate how autonomous agents can:
- classify and route customer requests
- invoke database‑backed support operations
- make confidence‑based escalation decisions
- persist memory across sessions
- log decisions for auditability

The implementation is intentionally enterprise‑oriented and aligns with
reviewer requirements for **routing, tools, memory, and observability**.

---

## 🧠 System Overview

Customer requests are handled as **tickets** and processed through a
graph‑based workflow of specialized agents.

High‑level flow:
User Input
|
v
Intent Agent
|
+-- knowledge_path --> Retrieval Agent --> Analysis Agent --> Memory Agent --> END
|
+-- account_path   --> Retrieval Agent --> Analysis Agent --> Memory Agent --> END
|
+-- escalation_path --------------------> Analysis Agent --> Memory Agent --> END

Routing decisions are based on:
- natural‑language intent
- ticket metadata such as urgency and complexity

---

## 🔑 Key Capabilities

### 🔀 Intelligent Routing
- Requests are classified into:
  - knowledge questions (FAQs, how‑to)
  - account‑specific actions (subscriptions, user details)
  - urgent or unclear requests
- Routing logic lives in a dedicated **Intent Agent**

---

### 🧰 Database‑Backed Support Tools
The system integrates multiple **DB‑backed tools**, including:

- Account lookup by email
- Subscription status retrieval
- Experience / reservation lookup

All database access is:
- abstracted behind tools
- structured in responses
- fully logged

---

### 🧠 Memory Architecture

#### Short‑Term (Session) Memory
- Implemented via a **LangGraph checkpointer**
- Identified by `thread_id` (ticket ID)
- Enables multi‑step workflows
- Allows workflow state inspection via `get_state_history()`

#### Long‑Term (Persistent) Memory
- Implemented using SQLite (`ticket_messages`)
- Stores user and assistant messages
- Retrieved across sessions for personalization and context reuse

Together, this enables:
- continuity within a session
- context awareness across sessions

---

### 📊 Logging & Observability
All major decisions are logged into SQLite (`ticket_logs`), including:
- intent classification
- routing decisions
- tools invoked
- confidence scores
- escalation outcomes

Logs are:
- persisted
- structured (JSON payloads)
- queryable by ticket or stage

This supports debugging, auditing, and reviewer inspection.

---

## 📁 Repository Structure

```text
solution/
├── agentic/
│   ├── agents/         # Core agents (intent, retrieval, analysis, memory)
│   ├── tools/          # DB-backed tools + logging + memory store
│   └── workflow.py     # LangGraph orchestration logic
│
├── design/             # System design documentation
│
├── data/
│   ├── external/       # CultPass source DB (read-only)
│   └── core/           # App-managed DB (logs + memory)
│
├── utils.py            # Chat interface and app bootstrap
├── 01_external_db_setup.ipynb
├── 02_core_db_setup.ipynb
└── 03_agentic_app.ipynb

# How to Run the Application

Initialize databases:

Run 01_external_db_setup.ipynb
Run 02_core_db_setup.ipynb


Open 03_agentic_app.ipynb
Start the application:

    app = orchestrator()
    chat_interface(app, "TICKET-001")

Use different ticket IDs (thread_id) to demonstrate:

session memory
persistent memory
log separation

# How to Inspect Memory & Logs

Inspect session state:

app.get_state(
    config={"configurable": {"thread_id": "TICKET-001"}}
)

Inspect Workflow History

list(
    app.get_state_history(
        config={"configurable": {"thread_id": "TICKET-001"}}
    )
)

Inspect Logs:

SELECT ticket_id, stage, payload, created_at
FROM ticket_logs
ORDER BY created_at DESC;
