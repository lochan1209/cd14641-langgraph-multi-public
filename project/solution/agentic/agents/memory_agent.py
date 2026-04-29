
def memory_agent(state, config):
    """
    Memory Agent – REQUIRED state mutation for LangGraph checkpoints
    """

    # ✅ Explicitly WRITE into state (not just return values)
    state["final_answer"] = state.get("final_answer")
    state["confidence"] = state.get("confidence")
    state["escalated"] = state.get("escalated")
    state["escalation_reason"] = state.get("escalation_reason")

    # Keep a compact summary for demos / audits
    state["conversation_summary"] = (
        f"confidence={state.get('confidence')}, escalated={state.get('escalated')}"
    )

    # Track execution path
    state["actions_taken"] = (state.get("actions_taken") or []) + ["memory_agent"]

    # ✅ MUST return mutated state
    return state
