
from typing import TypedDict, Annotated, List
import operator

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from agentic.agents.intent_agent import intent_agent
from agentic.agents.retrieval_agent import retrieval_agent
from agentic.agents.analysis_agent import analysis_agent
from agentic.agents.memory_agent import memory_agent


class AgentState(TypedDict):
    user_input: str
    intent: str
    retrieved_context: dict
    final_answer: str
    conversation_summary: str
    next_step: str
    actions_taken: Annotated[List[str], operator.add]


def route(state: AgentState) -> str:
    return state.get("next_step", "end")


def orchestrator():
    graph = StateGraph(AgentState)

    graph.add_node("intent", intent_agent)
    graph.add_node("retrieve", retrieval_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("memory", memory_agent)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        route,
        {"retrieve": "retrieve"}
    )

    graph.add_edge("retrieve", "analysis")
    graph.add_edge("analysis", "memory")
    graph.add_edge("memory", END)

    return graph.compile(checkpointer=MemorySaver())
