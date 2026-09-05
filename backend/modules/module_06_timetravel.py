"""Module 06 — Time Travel & State Rewinding.

Demonstrates LangGraph's checkpoint-based time travel capability. Each node
writes a state snapshot, and the full history can be browsed via
`get_state_history()` to rewind to any prior checkpoint and branch execution.

Graph topology: START → Step 1 → Step 2 → Step 3 → END (each checkpointed)
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

# Shared SQLite checkpointer to persist checkpoints across HTTP requests and prevent RAM OOM
_conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
shared_checkpointer = SqliteSaver(_conn)
shared_checkpointer.setup()

class State(TypedDict):
    """Time-travel state with step counter and accumulated data."""
    step_count: int
    data: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile a three-step checkpointed graph for time-travel demo.

    Args:
        api_key: Anthropic API key (unused in this module — deterministic steps).
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])
    checkpointer = shared_checkpointer

    def step_one(state: State):
        """First processing step — creates checkpoint 1."""
        count = state.get("step_count", 0) + 1
        data = state.get("data", "Initial Input")
        steps = state.get("execution_steps", [])
        steps.append(f"Step 1 (Checkpoint 1): Data = '{data}', count = {count}")
        return {"step_count": count, "data": f"{data} -> Step 1 Processed", "execution_steps": steps}

    def step_two(state: State):
        """Second processing step — creates checkpoint 2."""
        count = state.get("step_count", 0) + 1
        data = state.get("data", "")
        steps = state.get("execution_steps", [])
        steps.append(f"Step 2 (Checkpoint 2): Data = '{data}', count = {count}")
        return {"step_count": count, "data": f"{data} -> Step 2 Processed", "execution_steps": steps}

    def step_three(state: State):
        """Third processing step — creates final checkpoint 3."""
        count = state.get("step_count", 0) + 1
        data = state.get("data", "")
        steps = state.get("execution_steps", [])
        steps.append(f"Step 3 (Checkpoint 3 - Final): Data = '{data}', count = {count}")
        return {"step_count": count, "data": f"{data} -> Completed!", "execution_steps": steps}

    builder = StateGraph(State)
    builder.add_node("step_one", step_one)
    builder.add_node("step_two", step_two)
    builder.add_node("step_three", step_three)

    builder.add_edge(START, "step_one")
    builder.add_edge("step_one", "step_two")
    builder.add_edge("step_two", "step_three")
    builder.add_edge("step_three", END)

    graph = builder.compile(checkpointer=checkpointer)
    return graph, cb
