
# Support & Infrastructure Tools

This directory contains all **supporting tools** used by the agentic workflow.
These tools encapsulate **external data access**, **persistent memory**, and
**observability/logging**, allowing agents to focus purely on decision logic.

All tools return **structured outputs** and are safely integrated into the
LangGraph workflow.

---

## 🧰 Tool Categories

| Category | Tools |
|--------|------|
| Knowledge Retrieval | `retrieval_tool.py` |
| Account / Subscription | `account_lookup_tool.py`, `subscription_tool.py` |
| Memory Persistence | `memory_store.py` |
| Logging / Audit | `logger.py` |

---

## 📚 `retrieval_tool.py`

### Purpose
- Retrieves relevant help and FAQ articles
- Acts as the system’s knowledge base interface

### Usage Context
- Used by the **Retrieval Agent**
- Supports knowledge‑based customer questions

### Output Structure
- Ranked articles with:
  - title
  - snippet / content
  - relevance score

Design principle:
> Knowledge retrieval is isolated from reasoning logic to avoid agent hallucination.

---

## 👤 `account_lookup_tool.py`

### Purpose
- Looks up user records by email
- Retrieves linked subscription details

### Backing Store
- SQLite database: `data/external/cultpass.db`

### Usage Context
- Invoked for account‑specific requests only
- Handles input normalization and safe failures

### Output Structure
- `found`: boolean
- `user`: structured user record (if found)
- `subscription`: structured subscription record (if found)
- `error`: descriptive error message (if not found)

Design principle:
> Account actions are treated as sensitive operations and fail safely with escalation.

---

## 💳 `subscription_tool.py`

### Purpose
- Retrieves detailed subscription status
- Supplements account lookup with structured plan details

### Usage Context
- Optional secondary lookup for account workflows
- Supports richer, more accurate responses

---

## 💾 `memory_store.py`

### Purpose
- Implements **long‑term persistent memory**
- Stores and retrieves conversation history across sessions

### Backing Store
- SQLite database: `data/core/udahub.db`
- Table: `ticket_messages`

### Stored Fields
- `message_id` (generated UUID)
- `ticket_id`
- `role` (user / assistant)
- `content`
- `created_at`

### Usage Context
- Used by **Analysis Agent**
- Provides historical context (`PRIOR_HISTORY`) for personalized responses

Design principle:
> Persistent memory enables continuity across sessions, not just within a single workflow.

---

## 📊 `logger.py`

### Purpose
- Centralized structured logging for all agent decisions
- Enables observability, auditing, and debugging

### Backing Store
- SQLite database: `data/core/udahub.db`
- Table: `ticket_logs`

### Logged Events Include
- intent classification
- routing decisions
- tools invoked
- confidence scores
- escalation outcomes
- error conditions

### Output Format
- JSON payloads per log entry
- Searchable by `ticket_id` and `stage`

Design principle:
> All significant decisions must be auditable and queryable after execution.

---

## ✅ Tool Design Guarantees

- No agent directly accesses databases
- All data access is abstracted via tools
- Tools return structured, predictable outputs
- Errors are explicit and non‑fatal
- All tool usage is logged

---

## 🔍 Example: Testing Tool Integration

```python
Check subscription details for cathy.bloom@florals.org
