
# Tools

This folder contains **tool implementations** used by agents to abstract external operations such as data retrieval.

Tools provide a controlled interface between agents and data sources.

---

## Why Tools Exist
- Keep agents lightweight and focused on reasoning
- Abstract implementation details (files, DBs, APIs)
- Enable safe extension without changing agent logic

---

## Available Tools

### Retrieval Tool
**File:** `retrieval_tool.py`

**Purpose:**
- Simulate retrieval‑augmented generation (RAG)
- Fetch relevant context based on user queries
- Provide structured results to the Retrieval Agent

**Behavior:**
- Accepts a query string
- Returns a dictionary containing relevant content
- Can be extended to use embedding or vector search

---

## Design Considerations
- Tools do not manage workflow state
- Tools are stateless and reusable
- Tools are injected at runtime via LangGraph config

---

## Future Enhancements
- Semantic vector search
- Database query tools
- External API integrations

These are intentionally out of scope for this project.
