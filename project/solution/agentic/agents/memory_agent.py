
from langchain_core.runnables import RunnableConfig

def memory_agent(state, config: RunnableConfig):
    # Keep a short summary that includes escalation outcome
    escalated = state.get("escalated", False)
    conf = state.get("confidence", 0.0)

    summary = f"Resolved={not escalated}; Escalated={escalated}; Confidence={conf:.2f}"

    return {
        "conversation_summary": summary,
        "next_step": "end",
        "actions_taken": ["memory_agent"],
    }
