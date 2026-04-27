
from agentic.tools.retrieval_tool import retrieve_articles
from langchain_core.runnables import RunnableConfig

def retrieval_agent(state, config: RunnableConfig):
    results = retrieve_articles(state["user_input"])

    return {
        "retrieved_context": results,
        "next_step": "analysis",
        "actions_taken": ["retrieval_agent"],
    }
