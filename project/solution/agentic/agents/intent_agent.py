
def intent_agent(state, config):
    """
    Intent Agent

    Responsibilities:
    - Classify the ticket intent
    - Decide routing path (knowledge_path / account_path / escalation_path)
    - IMPORTANT: Pass through core state fields so downstream agents can read them
    """

    user_input = state.get("user_input", "")
    ticket_id = state.get("ticket_id")
    ticket_metadata = state.get("ticket_metadata", {}) or {}

    text = user_input.lower()
    urgency = ticket_metadata.get("urgency", "low").lower()

    # 1. Metadata-driven escalation (highest priority)
    if urgency == "high":
        intent = "urgent"
        next_step = "escalation_path"

    # 2. Account / action requests
    elif "@" in text or any(k in text for k in ["account", "subscription", "quota", "cancel"]):
        intent = "account_action"
        next_step = "account_path"

    # 3. Knowledge / QA requests
    elif any(k in text for k in ["how", "what", "where", "when", "reserve", "book", "event"]):
        intent = "qa"
        next_step = "knowledge_path"

    elif any(k in text for k in ["summarize", "summary"]):
        intent = "summarization"
        next_step = "knowledge_path"

    # 4. Fallback
    else:
        intent = "unknown"
        next_step = "escalation_path"

    return {
        # ✅ PASS THROUGH CORE STATE
        "ticket_id": ticket_id,
        "user_input": user_input,
        "ticket_metadata": ticket_metadata,

        # ✅ NEW INTENT FIELDS
        "intent": intent,
        "next_step": next_step,

        "actions_taken": ["intent_agent"],
    }
