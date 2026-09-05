"""Module 03b — Plan-and-Execute Agent.

Separates high-level planning from step-by-step task execution. The Planner
node creates a structured multi-step plan, the Executor runs steps one-by-one,
and the Replanner evaluates progress and dynamically updates remaining steps.

Graph topology: START → Planner → Executor ↔ Replanner → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List, Tuple
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Plan-and-execute agent state with plan steps and execution history."""
    input_query: str
    plan: List[str]
    past_steps: List[Tuple[str, str]]
    response: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the plan-and-execute agent graph.

    Args:
        api_key: Anthropic API key. If empty, uses deterministic fallback plan.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def planner_node(state: State):
        """Create a structured step-by-step plan for the user's query."""
        query = state["input_query"]
        steps = state.get("execution_steps", [])
        steps.append("Planner Node: Creating step-by-step execution plan...")

        if llm:
            res = llm.invoke([
                SystemMessage(content="Break down the request into 3 clear, sequential steps. Return each step on a new line prefixed with a number (e.g. 1. step)."),
                HumanMessage(content=query)
            ])
            lines = [line.strip() for line in extract_text_content(res.content).split("\n") if line.strip()]
            plan = [l for l in lines if l and l[0].isdigit()] or lines[:3]
        else:
            plan = [
                f"1. Research background information for '{query}'",
                f"2. Analyze key components of '{query}'",
                f"3. Formulate comprehensive answer for '{query}'"
            ]

        steps.append(f"Planner Node: Plan created with {len(plan)} steps.")
        return {"plan": plan, "past_steps": [], "execution_steps": steps}

    def executor_node(state: State):
        """Execute the current step of the plan."""
        plan = state["plan"]
        past_steps = state.get("past_steps", [])
        steps = state.get("execution_steps", [])

        current_step_index = len(past_steps)
        current_task = plan[current_step_index]
        steps.append(f"Executor Node: Executing step {current_step_index + 1}/{len(plan)}: '{current_task}'")

        if llm:
            res = llm.invoke([
                SystemMessage(content=f"Execute this step of the overall task: {current_task}"),
                HumanMessage(content=f"Original request: {state['input_query']}\nCompleted prior steps: {past_steps}")
            ])
            result = extract_text_content(res.content)
        else:
            result = f"[Executed]: Completed step '{current_task}' successfully."

        new_past_steps = past_steps + [(current_task, result)]
        steps.append(f"Executor Node: Step {current_step_index + 1} completed.")
        return {"past_steps": new_past_steps, "execution_steps": steps}

    def replanner_node(state: State):
        """Evaluate progress and determine whether to continue or finalize."""
        plan = state["plan"]
        past_steps = state["past_steps"]
        steps = state.get("execution_steps", [])
        steps.append("Replanner Node: Checking if plan is complete...")

        if len(past_steps) >= len(plan):
            steps.append("Replanner Node: All steps completed! Synthesizing final response.")
            final_summary = "\n\n".join([f"**{task}**\n{res}" for task, res in past_steps])
            return {"response": f"### Final Plan Execution Summary\n\n{final_summary}", "execution_steps": steps}

        steps.append(f"Replanner Node: {len(plan) - len(past_steps)} steps remaining. Continuing execution.")
        return {"execution_steps": steps}

    def should_continue(state: State):
        """Route back to executor if steps remain, otherwise finish."""
        plan = state["plan"]
        past_steps = state["past_steps"]
        if len(past_steps) < len(plan):
            return "executor"
        return END

    builder = StateGraph(State)
    builder.add_node("planner", planner_node)
    builder.add_node("executor", executor_node)
    builder.add_node("replanner", replanner_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "replanner")
    builder.add_conditional_edges("replanner", should_continue, {"executor": "executor", END: END})

    graph = builder.compile()
    return graph, cb
