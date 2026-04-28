
def memory_agent(state, config):
    """
    Memory Agent

    Responsibilities:
    - Persist conversation summaries / resolved outcomes
    - Preserve final response so it is returned to the user
    - Support long-term inspection and reuse of state
    """

    # ---- Preserve critical outputs from analysis_agent ----
    final_answer = state.get("final_answer")
    confidence = state.get("confidence")
    escalated = state.get("escalated")
    escalation_reason = state.get("escalation_reason")

    # Optional lightweight summary (for logs / DB storage)
    conversation_summary = (
        f"resolved={not escalated}, "
        f"escalated={escalated}, "
        f"confidence={confidence}"
    )

    result = {
        # ✅ MUST keep these, otherwise chat_interface prints "No response generated"
        "final_answer": final_answer,
        "confidence": confidence,
        "escalated": escalated,
        "escalation_reason": escalation_reason,

        # Memory artifact
        "conversation_summary": conversation_summary,

        "actions_taken": ["memory_agent"]
    }

    return result
