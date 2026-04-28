
import re
from langchain_core.runnables import RunnableConfig

from agentic.tools.retrieval_tool import retrieve_articles
from agentic.tools.account_lookup_tool import lookup_account

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def retrieval_agent(state, config: RunnableConfig):
    """
    Retrieval Agent

    Responsibilities:
    - Retrieve KB articles
    - Optionally perform account lookup
    - IMPORTANT: Pass through core state fields so downstream agents keep context
    """

    # --- Pass-through fields ---
    ticket_id = state.get("ticket_id")
    user_input = state.get("user_input", "")
    ticket_metadata = state.get("ticket_metadata", {})
    intent = state.get("intent")

    # --- KB retrieval ---
    kb = retrieve_articles(user_input, top_k=3)

    # --- Account lookup tool ---
    account_info = None
    if EMAIL_RE.search(user_input):
        account_info = lookup_account(user_input)

    tools_used = ["retrieve_articles"] + (["lookup_account"] if account_info else [])

    return {
        # ✅ PASS THROUGH CORE STATE
        "ticket_id": ticket_id,
        "user_input": user_input,
        "ticket_metadata": ticket_metadata,
        "intent": intent,

        # ✅ NEW DATA FROM THIS AGENT
        "retrieved_kb": kb,
        "account_info": account_info,
        "tools_used": tools_used,

        "next_step": "analysis",
        "actions_taken": ["retrieval_agent"],
    }
