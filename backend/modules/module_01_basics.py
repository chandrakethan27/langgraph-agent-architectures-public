"""Module 01 — Fundamentals: State, Nodes & Edges.

Demonstrates the simplest LangGraph pattern: a linear sequential graph where
the output of one node is passed as input to the next via a shared TypedDict
state. This is the foundational building block for all other architectures.

Graph topology: START → Generate Outline → Write Content → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Shared state schema for sequential content generation."""
    topic: str
    outline: str
    content: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile a sequential two-node content generation graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback responses.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def generate_outline(state: State):
        """Node 1: Generate a structured outline from the given topic."""
        topic = state["topic"]
        steps = state.get("execution_steps", [])
        steps.append("Node 1: generating outline...")
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="You are a helpful assistant. Provide a brief 3-bullet-point outline for the topic."),
                HumanMessage(content=f"Topic: {topic}")
            ])
            outline = extract_text_content(res.content)
        else:
            outline = f"1. Introduction to {topic}\n2. Key concepts of {topic}\n3. Conclusion and summary of {topic}"
            
        return {"outline": outline, "execution_steps": steps}

    def write_content(state: State):
        """Node 2: Draft final content based on the generated outline."""
        topic = state["topic"]
        outline = state["outline"]
        steps = state.get("execution_steps", [])
        steps.append("Node 2: drafting final content based on outline...")

        if llm:
            res = llm.invoke([
                SystemMessage(content="Write a concise paragraph expanding on the provided outline."),
                HumanMessage(content=f"Topic: {topic}\nOutline:\n{outline}")
            ])
            content = extract_text_content(res.content)
        else:
            content = f"Here is a comprehensive summary of {topic} based on the outline:\n\n{outline}\n\nThis concludes the generated content."

        return {"content": content, "execution_steps": steps}

    builder = StateGraph(State)
    builder.add_node("generate_outline", generate_outline)
    builder.add_node("write_content", write_content)
    
    builder.add_edge(START, "generate_outline")
    builder.add_edge("generate_outline", "write_content")
    builder.add_edge("write_content", END)

    graph = builder.compile()
    return graph, cb
