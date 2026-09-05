"""Module 12 — Context & Dependency Injection.

Demonstrates injecting external configuration (tenant IDs, database URLs,
feature toggles) into graph nodes at runtime via LangGraph's RunnableConfig,
without modifying the graph's state schema.

Graph topology: START → Context-Aware Node → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Context injection state with input text and processed output."""
    input_text: str
    output_result: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the context-aware dependency injection graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback responses.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def context_aware_node(state: State, config: RunnableConfig):
        """Process input using injected runtime configuration (tenant, DB, feature flags)."""
        text = state["input_text"]
        steps = state.get("execution_steps", [])

        # Extract injected context/configurable properties from RunnableConfig
        configurable = config.get("configurable", {})
        tenant_id = configurable.get("tenant_id", "default-tenant")
        database_url = configurable.get("database_url", "sqlite:///app.db")
        feature_flag_active = configurable.get("experimental_feature", False)

        steps.append(f"Context Node: Extracted injected RunnableConfig -> tenant_id='{tenant_id}', db='{database_url}', feature_flag={feature_flag_active}")

        if llm:
            res = llm.invoke([
                SystemMessage(content=f"You are operating under Tenant ID: {tenant_id}. Feature flag: {feature_flag_active}."),
                HumanMessage(content=text)
            ])
            out = extract_text_content(res.content)
        else:
            out = f"[Context Injected Result] Processed for Tenant '{tenant_id}' using DB '{database_url}'. Feature Flag Active: {feature_flag_active}."

        steps.append("Context Node: Execution complete without altering graph state schema.")
        return {"output_result": out, "execution_steps": steps}

    builder = StateGraph(State)
    builder.add_node("context_aware_node", context_aware_node)
    builder.add_edge(START, "context_aware_node")
    builder.add_edge("context_aware_node", END)

    graph = builder.compile()
    return graph, cb
