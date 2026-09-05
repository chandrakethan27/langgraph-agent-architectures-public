"""Module 05 — Guardrails & Human-in-the-Loop (HITL).

Demonstrates safety guardrails by using LangGraph's `interrupt_before` to halt
graph execution before executing dangerous or irreversible actions. A human
operator can review, approve, or reject the proposed action before resumption.

Graph topology: START → Propose Action ─( INTERRUPT )─→ Dangerous Action → END
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
    """HITL state with proposed action, approval flag, and status."""
    proposed_action: str
    is_approved: bool
    status_message: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the HITL graph with interrupt_before breakpoint.

    Args:
        api_key: Anthropic API key.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])
    checkpointer = shared_checkpointer

    def propose_action_node(state: State):
        """Generate or accept a proposed action and trigger the interrupt guardrail."""
        action = state.get("proposed_action", "DELETE FROM production_users WHERE active = false;")
        steps = state.get("execution_steps", [])
        steps.append(f"Propose Action Node: Agent generated sensitive command -> '{action}'")
        steps.append("GUARDRAIL TRIGGERED: Execution paused! Waiting for human approval in UI.")
        return {"proposed_action": action, "execution_steps": steps}

    def dangerous_action_node(state: State):
        """Execute or abort the action based on human approval decision."""
        approved = state.get("is_approved", False)
        action = state["proposed_action"]
        steps = state.get("execution_steps", [])
        
        if approved:
            steps.append(f"Human Guardrail: Action APPROVED by human. Executing -> '{action}'")
            msg = f"SUCCESS: Action '{action}' was executed safely following human authorization."
        else:
            steps.append(f"Human Guardrail: Action REJECTED by human. Aborting -> '{action}'")
            msg = f"CANCELLED: Action '{action}' was aborted per human instruction."
            
        return {"status_message": msg, "execution_steps": steps}

    builder = StateGraph(State)
    builder.add_node("propose_action_node", propose_action_node)
    builder.add_node("dangerous_action_node", dangerous_action_node)

    builder.add_edge(START, "propose_action_node")
    builder.add_edge("propose_action_node", "dangerous_action_node")
    builder.add_edge("dangerous_action_node", END)

    # Interrupt execution right before running the dangerous node
    graph = builder.compile(checkpointer=checkpointer, interrupt_before=["dangerous_action_node"])
    return graph, cb
