
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

def analysis_agent(state, config: RunnableConfig):
    llm = config["configurable"]["llm"]

    context = state.get("retrieved_context", {})
    user_input = state["user_input"]

    prompt = [
        SystemMessage(content="Use the retrieved context to answer the user."),
        SystemMessage(content=str(context)),
        HumanMessage(content=user_input),
    ]

    answer = llm.invoke(prompt).content

    return {
        "messages": [HumanMessage(content=user_input),],
        "final_answer": answer,
        "next_step": "memory",
        "actions_taken": ["analysis_agent"],
    }
