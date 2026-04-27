
"""
Custom LangGraph workflow for the Agentic AI project.

Rules satisfied:
- Graph is built from scratch (NO create_react_agent / NO prebuilt workflow)
- Agents live in agentic/agents
- Tools live in agentic/tools
- Short-term memory via thread_id + checkpointer
"""

from __future__ import annotations

from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# -----------------------------
# TODO: Import your agents
# Example (rename to match your files):
# from agentic.agents.intent_agent import classify_intent
# from agentic.agents.retrieval_agent import retrieve_context
# from agentic.agents.analysis_agent import analyze
# from agentic.agents.action_agent import generate_response
# from agentic.agents.memory_agent import write_memory
# -----------------------------

# -----------------------------
# TODO: Import your tools
# Example:
# from agentic.tools.db_tools import search_articles, read_customer_profile
# -----------------------------


class WorkflowState(TypedDict):
    """
    Shared state across the workflow.
    Keep it small, explicit, and testable.
    """
    # Conversation
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str

    # Routing / intent
    intent: Optional[str]          # e.g., "qa", "support", "action", "unknown"
    next_step: str                # node name to route to

    # Retrieval / reasoning
    retrieved_context: Optional[Dict[str, Any]]  # docs, rows, passages
    answer: Optional[str]

    # Memory
    short_summary: Optional[str]
    long_term_keys: Optional[List[str]]

    # Observability
    actions_taken: Annotated[List[str], operator.add]


# -----------------------------
# Minimal default node helpers
# -----------------------------

def _ensure_user_message(state: WorkflowState) -> List[BaseMessage]:
    """
    Ensure the user's current input is present as a HumanMessage in the message list.
    """
    msgs = state.get("messages", [])
    if not msgs or not isinstance(msgs[-1], HumanMessage) or msgs[-1].content != state["user_input"]:
        msgs = msgs + [HumanMessage(content=state["user_input"])]
    return msgs


# -----------------------------
# Node 1: Intent classification
# -----------------------------
def intent_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """
    Uses LLM to classify intent. Output stored in state.intent and state.next_step.

    IMPORTANT:
    - Uses config["configurable"]["llm"]
    - Uses conversation context from state.messages
    """
    llm = config.get("configurable", {}).get("llm")
    messages = _ensure_user_message(state)

    # Simple prompt – replace with your Intent Agent prompt/schema if needed
    system = SystemMessage(content=(
        "You are an intent classifier for the Uda-hub assistant. "
        "Classify the user request into one of: qa, summarization, action, unknown. "
        "Return ONLY the label."
    ))

    label = llm.invoke([system] + messages).content.strip().lower()

    if label not in {"qa", "summarization", "action", "unknown"}:
        label = "unknown"

    # Route to the correct agent node
    if label == "summarization":
        next_step = "retrieval_node"
    elif label == "action":
        next_step = "retrieval_node"
    else:
        next_step = "retrieval_node"  # default still retrieves (safe)

    return {
        "messages": messages,
        "intent": label,
        "next_step": next_step,
        "actions_taken": ["intent_node"]
    }


# -----------------------------
# Node 2: Retrieval (DB / RAG)
# -----------------------------
def retrieval_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """
    Retrieves relevant context from DB / vector index / files.

    Replace the stub retrieval with your real tool calls.
    """
    tools = config.get("configurable", {}).get("tools", [])
    llm = config.get("configurable", {}).get("llm")

    messages = _ensure_user_message(state)

    # Minimal tool-agnostic retrieval pattern:
    # We ask the model to decide what to retrieve, then call your retrieval tools in code.
    # For now, a placeholder structure so the graph is runnable.
    retrieved = {
        "notes": "TODO: Replace with real retrieval (db + RAG).",
        "items": []
    }

    # Route to analysis
    return {
        "messages": messages,
        "retrieved_context": retrieved,
        "next_step": "analysis_node",
        "actions_taken": ["retrieval_node"]
    }


# -----------------------------
# Node 3: Analysis / reasoning
# -----------------------------
def analysis_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """
    Uses LLM to reason over retrieved_context and decide what to do next.
    """
    llm = config.get("configurable", {}).get("llm")
    messages = _ensure_user_message(state)
    context = state.get("retrieved_context", {})

    system = SystemMessage(content=(
        "You are an analyst agent. Use the retrieved context to prepare the best possible answer. "
        "If context is insufficient, clearly say what is missing."
    ))

    # Put retrieved context as a system message so the model can use it
    context_msg = SystemMessage(content=f"RETRIEVED_CONTEXT:\n{context}")

    draft = llm.invoke([system, context_msg] + messages).content

    return {
        "messages": messages + [AIMessage(content=draft)],
        "answer": draft,
        "next_step": "memory_node",
        "actions_taken": ["analysis_node"]
    }


# -----------------------------
# Node 4: Memory update
# -----------------------------
def memory_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """
    Summarizes the turn and stores memory signals.
    - short-term: stays in checkpointed state (thread_id)
    - long-term: you can write embeddings / store semantic memory (TODO)
    """
    llm = config.get("configurable", {}).get("llm")
    messages = state.get("messages", [])

    system = SystemMessage(content=(
        "Summarize this conversation turn in 2-3 lines. "
        "Also output any long-term memory keys (comma-separated) if relevant, else NONE."
    ))
    summary = llm.invoke([system] + messages).content.strip()

    # Simple parse for long-term keys (optional)
    long_term_keys: List[str] = []
    if "NONE" not in summary.upper():
        # keep it minimal; you can replace with structured output later
        pass

    return {
        "short_summary": summary,
        "long_term_keys": long_term_keys,
        "next_step": "end",
        "actions_taken": ["memory_node"]
    }


# -----------------------------
# Router
# -----------------------------
def route(state: WorkflowState) -> str:
    """
    Determines which node to execute next.
    Must return a node name OR 'end'.
    """
    return state.get("next_step", "end")


# -----------------------------
# Public: build the workflow
# -----------------------------
def build_workflow() -> Any:
    """
    Builds and compiles the LangGraph workflow with MemorySaver checkpointer.
    You must pass config={"configurable": {"thread_id": ..., "llm": ..., "tools": ...}} at invoke time.
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("intent_node", intent_node)
    graph.add_node("retrieval_node", retrieval_node)
    graph.add_node("analysis_node", analysis_node)
    graph.add_node("memory_node", memory_node)

    graph.set_entry_point("intent_node")

    graph.add_conditional_edges(
        "intent_node",
        route,
        {
            "retrieval_node": "retrieval_node",
            "end": END
        }
    )

    graph.add_edge("retrieval_node", "analysis_node")
    graph.add_edge("analysis_node", "memory_node")
    graph.add_edge("memory_node", END)

    return graph.compile(checkpointer=MemorySaver())
