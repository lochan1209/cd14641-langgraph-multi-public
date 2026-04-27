
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig


def _confidence_from_kb(kb: dict) -> float:
    """Derive a simple confidence score from KB retrieval scores."""
    results = (kb or {}).get("results", [])
    if not results:
        return 0.20
    best = max(float(r.get("score", 0.0)) for r in results)
    bonus = min(0.20, 0.05 * max(0, len(results) - 1))  # small boost if multiple hits
    return float(min(1.0, best + bonus))


def analysis_agent(state, config: RunnableConfig):
    """
    Analysis agent:
    - If account_info is present and found=True, answer using account lookup (Tool #2) directly
    - Else answer using KB (Tool #1)
    - If KB confidence is low, escalate with confidence score
    """
    llm = config["configurable"]["llm"]

    user_input = state.get("user_input", "")
    kb = state.get("retrieved_kb", {}) or {}
    account_info = state.get("account_info")

    # -------------------------------
    # 1) TOOL #2 PRIORITY: Account lookup
    # -------------------------------
    # If user provided an email, retrieval_agent will attempt lookup_account().
    if account_info is not None:
        # Case A: Found user successfully
        if account_info.get("found"):
            user = account_info.get("user") or {}
            sub = account_info.get("subscription")

            if sub:
                final_answer = (
                    f"Here are the subscription details for {user.get('full_name', 'the customer')}:\n\n"
                    f"- Email: {user.get('email')}\n"
                    f"- Subscription Tier: {sub.get('tier')}\n"
                    f"- Status: {sub.get('status')}\n"
                    f"- Monthly Quota: {sub.get('monthly_quota')}\n\n"
                    "If you’d like help changing, pausing, or canceling the subscription, tell me what you want to do."
                )
                return {
                    "final_answer": final_answer,
                    "confidence": 0.95,
                    "escalated": False,
                    "escalation_reason": None,
                    "next_step": "memory",
                    "actions_taken": ["analysis_agent"],
                }

            # Found user but no subscription record
            final_answer = (
                f"I found the account for {user.get('email')}, but I couldn't find an associated subscription record.\n\n"
                "✅ Next step: Escalating to human support to validate account/subscription data.\n"
                "(confidence=0.55)"
            )
            return {
                "final_answer": final_answer,
                "confidence": 0.55,
                "escalated": True,
                "escalation_reason": "Account found but subscription missing",
                "next_step": "memory",
                "actions_taken": ["analysis_agent"],
            }

        # Case B: Account lookup attempted but failed
        

        err = account_info.get("error") or "Account lookup failed."
        dbg = account_info.get("debug", {}) or {}
        hint = ""
        if dbg:
            hint = (
                f"\n\n[debug]\n- db_path: {dbg.get('db_path')}\n"
                f"- tables: {dbg.get('tables')}\n"
                f"- total_users: {dbg.get('total_users')}\n"
                f"- sample_emails: {dbg.get('sample_emails')}\n"
            )

        final_answer = (
            "I tried to look up the account details, but I couldn't complete the account lookup.\n\n"
            f"Reason: {err}"
            f"{hint}\n"
            "✅ Next step: Escalating to human support.\n"
            "Please confirm the customer email and try again.\n"
            "(confidence=0.40)"
        )

        return {
            "final_answer": final_answer,
            "confidence": 0.40,
            "escalated": True,
            "escalation_reason": "Account lookup failed",
            "next_step": "memory",
            "actions_taken": ["analysis_agent"],
        }

    # -------------------------------
    # 2) TOOL #1: Knowledge base answer + escalation
    # -------------------------------
    confidence = _confidence_from_kb(kb)
    escalation_threshold = 0.50
    kb_results = kb.get("results", []) or []

    if confidence < escalation_threshold:
        final_answer = (
            "I couldn't find a confident match in the knowledge base for this request.\n\n"
            "✅ Next step: Escalating to human support.\n"
            "To help resolve faster, please share one of the following:\n"
            "- the customer email (if account-specific)\n"
            "- the exact error message or screenshot (if technical)\n"
            "- what action you were trying to perform and when\n\n"
            f"(confidence={confidence:.2f})"
        )
        return {
            "final_answer": final_answer,
            "confidence": confidence,
            "escalated": True,
            "escalation_reason": "Low confidence knowledge match",
            "next_step": "memory",
            "actions_taken": ["analysis_agent"],
        }

    # Build KB context for the LLM (grounded answering)
    kb_context = "\n\n".join(
        [f"- {r['title']} (score={r['score']}): {r.get('full_content', r.get('snippet', ''))}" for r in kb_results]
    ) or "No KB context."

    system = SystemMessage(content=(
        "You are a customer support assistant for CultPass/Uda-hub.\n"
        "Answer using ONLY the provided KB_CONTEXT.\n"
        "If the KB_CONTEXT does not contain the answer, say so and suggest escalation.\n"
        "Be concise, accurate, and actionable."
    ))

    prompt = [
        system,
        SystemMessage(content=f"KB_CONTEXT:\n{kb_context}"),
        HumanMessage(content=user_input),
    ]

    answer = llm.invoke(prompt).content.strip()

    # Cite KB sources by title (transparent grounding)
    cited_titles = [r.get("title") for r in kb_results if r.get("title")]
    if cited_titles:
        answer += "\n\nSources: " + "; ".join(cited_titles)
    answer += f"\n(confidence={confidence:.2f})"

    return {
        "final_answer": answer,
        "confidence": confidence,
        "escalated": False,
        "escalation_reason": None,
        "next_step": "memory",
        "actions_taken": ["analysis_agent"],
    }
