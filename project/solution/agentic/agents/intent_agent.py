
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

def intent_agent(state, config: RunnableConfig):
    llm = config["configurable"]["llm"]

    user_input = state["user_input"]

    prompt = [
        SystemMessage(content=(
            "Classify the user intent into one of: "
            "qa, summarization, action, unknown. "
            "Return ONLY the label."
        )),
        HumanMessage(content=user_input),
    ]

    intent = llm.invoke(prompt).content.strip().lower()

    if intent not in {"qa", "summarization", "action", "unknown"}:
        intent = "unknown"

    return {
        "intent": intent,
        "next_step": "retrieve",
        "actions_taken": ["intent_agent"],
    }
