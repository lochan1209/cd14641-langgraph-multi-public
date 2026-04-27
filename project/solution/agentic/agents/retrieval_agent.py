
import re
from langchain_core.runnables import RunnableConfig

from agentic.tools.retrieval_tool import retrieve_articles
from agentic.tools.account_lookup_tool import lookup_account

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def retrieval_agent(state, config: RunnableConfig):
    user_input = state["user_input"]

    kb = retrieve_articles(user_input, top_k=3)

    # Tool #2: account lookup only if email present (action/support use-case)
    account_info = None
    if EMAIL_RE.search(user_input):
        account_info = lookup_account(user_input)

    tools_used = ["retrieve_articles"] + (["lookup_account"] if account_info else [])

    return {
        "retrieved_kb": kb,
        "account_info": account_info,
        "tools_used": tools_used,
        "next_step": "analysis",
        "actions_taken": ["retrieval_agent"],
    }
