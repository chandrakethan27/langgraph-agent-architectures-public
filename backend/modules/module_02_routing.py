"""Module 02 — Decision Making: Conditional Edges (Routing).

Implements dynamic graph routing using intent classification. A classifier
node evaluates the user's input and conditionally routes to specialized expert
nodes (math, code, or general) via LangGraph conditional edges.

Graph topology: START → Classify Intent → {Math | Code | General} Expert → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Routing agent state with intent category and expert response."""
    input_prompt: str
    category: str
    response: str
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the intent routing graph with conditional expert branches.

    Args:
        api_key: Anthropic API key. If empty, uses keyword-based fallback classification.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def classify_intent(state: State):
        """Classify the user's input into one of: math, code, or general."""
        prompt = state["input_prompt"]
        steps = state.get("execution_steps", [])
        steps.append("Classifier Node: Analyzing intent...")

        if llm:
            res = llm.invoke([
                SystemMessage(content="Classify the input into exactly one category: 'math', 'code', or 'general'. Respond with only the single lowercase word without markdown or punctuation."),
                HumanMessage(content=prompt)
            ])
            raw_category = extract_text_content(res.content).strip().lower().replace("*", "").replace("`", "").replace('"', '').replace("'", "")
            if "math" in raw_category:
                category = "math"
            elif "code" in raw_category:
                category = "code"
            else:
                category = "general"
        else:
            if any(term in prompt.lower() for term in ["+", "-", "*", "/", "solve", "math", "equation"]):
                category = "math"
            elif any(term in prompt.lower() for term in ["python", "code", "function", "bug", "script", "js", "html"]):
                category = "code"
            else:
                category = "general"

        steps.append(f"Classifier Node: Category determined as '{category}'")
        return {"category": category, "execution_steps": steps}

    def math_expert(state: State):
        """Solve mathematical problems with step-by-step reasoning."""
        prompt = state["input_prompt"]
        steps = state.get("execution_steps", [])
        steps.append("Math Expert Node: Solving mathematical prompt...")
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="You are a math expert. Solve the problem step-by-step."),
                HumanMessage(content=prompt)
            ])
            ans = extract_text_content(res.content)
        else:
            ans = f"[Math Expert] Calculated answer for: '{prompt}' using step-by-step arithmetic."
            
        return {"response": ans, "execution_steps": steps}

    def code_expert(state: State):
        """Write clean, commented code solutions."""
        prompt = state["input_prompt"]
        steps = state.get("execution_steps", [])
        steps.append("Code Expert Node: Writing code solution...")
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="You are a senior software developer. Write clean, commented code."),
                HumanMessage(content=prompt)
            ])
            ans = extract_text_content(res.content)
        else:
            ans = f"```python\n# [Code Expert] Generated code for: {prompt}\ndef solution():\n    return 'Done'\n```"

        return {"response": ans, "execution_steps": steps}

    def general_assistant(state: State):
        """Provide helpful answers for general knowledge questions."""
        prompt = state["input_prompt"]
        steps = state.get("execution_steps", [])
        steps.append("General Assistant Node: Formulating response...")
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="You are a helpful general assistant."),
                HumanMessage(content=prompt)
            ])
            ans = extract_text_content(res.content)
        else:
            ans = f"[General Assistant] Here is a helpful answer to your question: '{prompt}'"

        return {"response": ans, "execution_steps": steps}

    def route_intent(state: State) -> Literal["math_expert", "code_expert", "general_assistant"]:
        """Route to the appropriate expert node based on classified category."""
        cat = state.get("category", "general")
        if cat == "math":
            return "math_expert"
        elif cat == "code":
            return "code_expert"
        return "general_assistant"

    builder = StateGraph(State)
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("math_expert", math_expert)
    builder.add_node("code_expert", code_expert)
    builder.add_node("general_assistant", general_assistant)

    builder.add_edge(START, "classify_intent")
    builder.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "math_expert": "math_expert",
            "code_expert": "code_expert",
            "general_assistant": "general_assistant"
        }
    )

    builder.add_edge("math_expert", END)
    builder.add_edge("code_expert", END)
    builder.add_edge("general_assistant", END)

    graph = builder.compile()
    return graph, cb
