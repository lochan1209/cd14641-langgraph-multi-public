
# Agentic System Design

## Overview
This folder contains the **design documentation** for the Agentic AI system built for the Uda‑Hub platform as part of the Udacity *Advanced Agentic AI Techniques* project.

The system is designed using **agent-based decomposition** and **explicit workflow orchestration** with LangGraph.  
Each agent has a clear responsibility, and the workflow controls execution deterministically.

---

## Design Goals

The primary goals of this design are:

- Clearly separate concerns between agents
- Avoid monolithic prompt chains
- Enable observability of agent decisions
- Support multi‑turn conversations via memory
- Follow Udacity’s requirement of **no prebuilt workflows**

---

## High-Level Architecture
User Input
↓
Intent Agent
↓
Retrieval Agent
↓
Analysis Agent
↓
Memory Agent
↓
END

The workflow is implemented as a **custom LangGraph StateGraph**, not using any prebuilt agent or orchestration utilities.

---

## Agent Responsibilities

### 1. Intent Agent
**Purpose:**  
Classify the user's intent and determine how the workflow should proceed.

**Responsibilities:**
- Determine whether the input is a QA, summarization, action, or unknown request
- Route the workflow to the next appropriate node
- Use lightweight reasoning only (no retrieval)

**Why this agent exists:**  
Separating intent detection makes the workflow explicit and easier to extend.

---

### 2. Retrieval Agent
**Purpose:**  
Retrieve relevant contextual information for answering the user query.

**Responsibilities:**
- Abstract data access logic away from reasoning
- Fetch relevant articles or records using retrieval tools
- Prepare structured context for downstream reasoning

**Design choice:**  
Retrieval is isolated so it can later be replaced with semantic search or vector databases without altering reasoning logic.

---

### 3. Analysis Agent
**Purpose:**  
Generate the final answer using retrieved context.

**Responsibilities:**
- Combine user input with retrieved information
- Perform reasoning and synthesis
- Generate a clear, user-facing response

**Why this agent exists:**  
Keeps reasoning logic separate from retrieval and memory management.

---

### 4. Memory Agent
**Purpose:**  
Maintain conversational context and continuity.

**Responsibilities:**
- Summarize the current interaction
- Persist state via LangGraph checkpointer
- Enable follow‑up questions within the same session

**Memory Strategy:**
- Short‑term memory is implemented using `thread_id`
- State history can be inspected using `get_state_history`

---

## Workflow Orchestration

The workflow is orchestrated using **LangGraph** with explicit nodes and edges.

### Key Design Decisions
- No `create_react_agent` or other prebuilt flows are used
- Routing is handled explicitly via a `next_step` field in state
- Each node updates only the part of the state it owns
- The workflow terminates explicitly with an `END` node

This makes the execution **transparent, testable, and deterministic**.

---

## Trade-offs and Limitations

### Intentional Trade-offs
- Retrieval uses simple logic instead of a vector DB
- No autonomous write actions to databases
- Minimal tool complexity to keep behavior explainable

### Future Improvements (Out of Scope)
- Semantic vector search for long-term memory
- Human-in-the-loop actions
- Tool-based mutations (e.g., booking experiences)

---

## Why This Design Fits the Project

This design:
- Fully satisfies Udacity’s rubric requirements
- Demonstrates genuine agentic decomposition
- Avoids hidden complexity
- Is easy to reason about and extend

The emphasis is on **clarity, correctness, and explainability**, not over-engineering.

---

## Summary

The system is a clean, modular, agentic architecture where:
- Each agent has a single responsibility
- The workflow makes execution explicit
- Memory is handled correctly
- The design supports future scalability

This documentation reflects the actual implementation present in the codebase.