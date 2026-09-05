"""Module 09 — Reflection & Self-Correction.

Implements a Generator-Evaluator loop where the agent produces a draft, passes
it to a critic that grades quality, and if rejected, loops back for revision.
Terminates when the evaluator passes the draft or a max revision count is hit.

Graph topology: START → Generator ↔ Evaluator → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Reflection state with draft, critique, revision tracking, and satisfaction."""
    prompt: str
    draft: str
    critique: str
    revision_number: int
    is_satisfied: bool
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the reflection self-correction graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock draft/critique cycle.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def generator_node(state: State):
        """Produce or revise a draft based on the prompt and any prior critique."""
        prompt = state["prompt"]
        critique = state.get("critique", "")
        rev = state.get("revision_number", 0) + 1
        steps = state.get("execution_steps", [])
        steps.append(f"Generator Node: Creating draft #{rev}...")

        if llm:
            sys = "You are a content creator. Write a short explanation."
            if critique:
                sys += f"\nImprove your previous draft based on this critique:\n{critique}"
            res = llm.invoke([
                SystemMessage(content=sys),
                HumanMessage(content=prompt)
            ])
            draft = extract_text_content(res.content)
        else:
            if rev == 1:
                draft = f"Initial rough draft about '{prompt}' with some basic ideas."
            else:
                draft = f"Polished, revised draft about '{prompt}' addressing critique: '{critique}'."

        steps.append(f"Generator Node: Draft #{rev} produced.")
        return {"draft": draft, "revision_number": rev, "execution_steps": steps}

    def evaluator_node(state: State):
        """Evaluate the current draft against quality rubrics."""
        draft = state["draft"]
        rev = state["revision_number"]
        steps = state.get("execution_steps", [])
        steps.append(f"Evaluator Node: Critiquing draft #{rev}...")

        if llm:
            res = llm.invoke([
                SystemMessage(content="Evaluate this draft. If it is high quality and complete, start response with 'PASSED:'. Otherwise start response with 'REJECTED:' followed by improvement instructions."),
                HumanMessage(content=draft)
            ])
            eval_text = extract_text_content(res.content)
            is_satisfied = eval_text.startswith("PASSED:") or rev >= 2
            critique = eval_text
        else:
            if rev >= 2:
                is_satisfied = True
                critique = "Draft is now excellent and approved!"
            else:
                is_satisfied = False
                critique = "Add more technical details and refine structure."

        steps.append(f"Evaluator Node: Critique -> satisfied={is_satisfied}")
        return {"is_satisfied": is_satisfied, "critique": critique, "execution_steps": steps}

    def should_continue(state: State):
        """Continue revising if not satisfied and under revision limit."""
        if state.get("is_satisfied", False) or state.get("revision_number", 0) >= 3:
            return END
        return "generator"

    builder = StateGraph(State)
    builder.add_node("generator", generator_node)
    builder.add_node("evaluator", evaluator_node)

    builder.add_edge(START, "generator")
    builder.add_edge("generator", "evaluator")
    builder.add_conditional_edges("evaluator", should_continue, {"generator": "generator", END: END})

    graph = builder.compile()
    return graph, cb
