
from langchain_core.runnables import RunnableConfig

def memory_agent(state, config: RunnableConfig):
    return {
        "conversation_summary": state.get("final_answer", ""),
        "next_step": "end",
        "actions_taken": ["memory_agent"],
    }
