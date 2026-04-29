
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agentic.agents.intent_agent import intent_agent
from agentic.agents.retrieval_agent import retrieval_agent
from agentic.agents.analysis_agent import analysis_agent
from agentic.agents.memory_agent import memory_agent


def route(state: dict) -> str:
    return state.get("next_step", "escalation_path")


def orchestrator():
    graph = StateGraph(dict)

    # Nodes
    graph.add_node("intent", intent_agent)
    graph.add_node("retrieve", retrieval_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("memory", memory_agent)

    graph.set_entry_point("intent")

    # Conditional routing based on intent + metadata decisions computed in intent_agent
    graph.add_conditional_edges(
        "intent",
        route,
        {
            "knowledge_path": "retrieve",
            "account_path": "retrieve",
            "escalation_path": "analysis",
        },
    )

    # Shared flow after retrieval
    graph.add_edge("retrieve", "analysis")
    graph.add_edge("analysis", "memory")
    graph.add_edge("memory", END)

    # Critical for reviewer spec:
    # Enables session inspection via thread_id and get_state_history()
    return graph.compile(checkpointer=MemorySaver())
