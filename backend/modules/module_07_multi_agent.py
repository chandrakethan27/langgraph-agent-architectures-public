"""Module 07 — Multi-Agent Supervisor Architecture.

Orchestrates multiple specialized worker agents via a central Supervisor that
evaluates progress, delegates tasks to the appropriate specialist (Researcher
or Coder), and determines when the workflow is complete.

Graph topology: START → Supervisor ↔ {Researcher | Coder} → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Multi-agent state with task, research notes, and code output."""
    task: str
    research_notes: str
    code_output: str
    next_worker: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the supervisor-worker multi-agent graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback responses.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def supervisor_node(state: State):
        """Central coordinator that evaluates progress and delegates to workers."""
        task = state["task"]
        notes = state.get("research_notes", "")
        code = state.get("code_output", "")
        steps = state.get("execution_steps", [])
        steps.append("Supervisor Node: Evaluating work done by team...")

        if not notes:
            next_w = "researcher"
            steps.append("Supervisor Node: Delegating task to 'Researcher' worker...")
        elif not code:
            next_w = "coder"
            steps.append("Supervisor Node: Research complete! Delegating to 'Coder' worker...")
        else:
            next_w = "FINISH"
            steps.append("Supervisor Node: Research & Code complete! Workflow finished.")

        return {"next_worker": next_w, "execution_steps": steps}

    def researcher_node(state: State):
        """Specialist worker that conducts research on the given task."""
        task = state["task"]
        steps = state.get("execution_steps", [])
        steps.append("Researcher Node: Conducting research on request...")

        if llm:
            res = llm.invoke([
                SystemMessage(content="You are a research specialist. Provide 2 key bullet points of facts on the topic."),
                HumanMessage(content=task)
            ])
            notes = extract_text_content(res.content)
        else:
            notes = f"- Key Research Fact 1 regarding '{task}'\n- Key Technical Spec 2 regarding '{task}'"

        steps.append("Researcher Node: Research completed. Returning findings to Supervisor.")
        return {"research_notes": notes, "execution_steps": steps}

    def coder_node(state: State):
        """Specialist worker that writes code based on research findings."""
        task = state["task"]
        notes = state["research_notes"]
        steps = state.get("execution_steps", [])
        steps.append("Coder Node: Writing python implementation using research notes...")

        if llm:
            res = llm.invoke([
                SystemMessage(content="You are a software engineer. Write a Python snippet based on the research notes."),
                HumanMessage(content=f"Task: {task}\nResearch:\n{notes}")
            ])
            code = extract_text_content(res.content)
        else:
            code = f"```python\n# Implementation based on research:\n# {notes.replace(chr(10), ' ')}\ndef run_solution():\n    print('Executed successfully!')\n```"

        steps.append("Coder Node: Code generated. Returning implementation to Supervisor.")
        return {"code_output": code, "execution_steps": steps}

    def route_supervisor(state: State) -> Literal["researcher", "coder", "__end__"]:
        """Route to the next worker or finish based on supervisor decision."""
        w = state.get("next_worker", "FINISH")
        if w == "researcher":
            return "researcher"
        elif w == "coder":
            return "coder"
        return END

    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_supervisor, {"researcher": "researcher", "coder": "coder", END: END})
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("coder", "supervisor")

    graph = builder.compile()
    return graph, cb
