"""Module 03 — ReAct Agent: Tool Calling Loop.

Implements the classic Reasoning + Action (ReAct) pattern where an autonomous
agent iterates through a think → act → observe cycle. The agent reasons about
the problem, calls external tools (calculator, web search, clock), observes the
results, and repeats until a final answer is ready.

Graph topology: START → Agent Node ↔ Tool Node → END (cyclic)
"""

from utils.text_helper import extract_text_content
import ast
import datetime
import logging
import operator as op
from typing import Annotated, TypedDict, List, Dict, Any
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from utils.llm_factory import get_llm
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

# Maximum number of agent↔tool iterations before forced termination
MAX_ITERATIONS = 10

# --- Safe math operators for AST-based evaluation ---
_SAFE_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
}

def _safe_eval_node(node: ast.AST) -> float:
    """Recursively evaluate an AST node using only safe arithmetic operators."""
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body)
    elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        return _SAFE_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_safe_eval_node(node.operand))
    else:
        raise ValueError(f"Unsupported expression node: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluates a mathematical expression safely using AST parsing.

    Only supports basic arithmetic: +, -, *, /, **, %. No function calls,
    variable access, or arbitrary code execution.
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval_node(tree)
        return str(result)
    except (ValueError, TypeError, SyntaxError, ZeroDivisionError) as e:
        logger.warning("Calculator evaluation failed for '%s': %s", expression, e)
        return f"Error evaluating expression: {str(e)}"

@tool
def search_web(query: str) -> str:
    """Mock web search tool returning factual context."""
    q = query.lower()
    if "weather" in q:
        return "The current weather in San Francisco is 68°F and sunny."
    elif "langgraph" in q:
        return "LangGraph is a Python/JS library for building stateful, multi-actor applications with LLMs, created by LangChain."
    elif "population" in q:
        return "The estimated population of Tokyo is 14 million."
    return f"Search results for '{query}': Found 3 relevant articles discussing {query}."

@tool
def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [calculator, search_web, get_current_time]
tools_by_name = {t.name: t for t in tools}

class State(TypedDict):
    """ReAct agent state with message history and iteration tracking."""
    messages: Annotated[List[BaseMessage], add_messages]
    execution_steps: List[str]
    iteration_count: int

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the ReAct agent graph with tool-calling cycle.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback responses.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    logger.info("Building ReAct agent graph with model=%s", model_name)
    
    if api_key:
        llm = get_llm(model_name, api_key, callbacks=[cb]).bind_tools(tools)
    else:
        llm = None

    def agent_node(state: State):
        """Core reasoning node — decides whether to call a tool or return a final answer."""
        messages = state["messages"]
        steps = state.get("execution_steps", [])
        iteration = state.get("iteration_count", 0) + 1
        steps.append(f"Agent Node (iteration {iteration}/{MAX_ITERATIONS}): Evaluating message history ({len(messages)} messages)...")

        # Safety guard: force termination after MAX_ITERATIONS
        if iteration > MAX_ITERATIONS:
            logger.warning("ReAct agent hit max iteration limit (%d). Forcing termination.", MAX_ITERATIONS)
            steps.append(f"Agent Node: MAX_ITERATIONS ({MAX_ITERATIONS}) reached — forcing final answer.")
            return {
                "messages": [AIMessage(content="I've reached my maximum reasoning steps. Based on what I've gathered so far, here is my best answer.")],
                "execution_steps": steps,
                "iteration_count": iteration,
            }
        
        if llm:
            response = llm.invoke(messages)
        else:
            # Fallback mock react loop
            last_user_msg = [m for m in messages if isinstance(m, HumanMessage)][-1].content.lower()
            if "weather" in last_user_msg and not any(isinstance(m, ToolMessage) for m in messages):
                response = AIMessage(content="", tool_calls=[{"name": "search_web", "args": {"query": "weather in San Francisco"}, "id": "call_1"}])
            elif "2" in last_user_msg or "+" in last_user_msg:
                response = AIMessage(content="", tool_calls=[{"name": "calculator", "args": {"expression": "25 * 4"}, "id": "call_2"}])
            else:
                response = AIMessage(content="I am a ReAct agent. I can use tools like search_web, calculator, and get_current_time to solve your requests!")

        if response.tool_calls:
            for tc in response.tool_calls:
                steps.append(f"Agent Node: Decided to call tool '{tc['name']}' with args {tc['args']}")
        else:
            steps.append("Agent Node: Generated final answer without further tool calls.")

        return {"messages": [response], "execution_steps": steps, "iteration_count": iteration}

    def tool_node(state: State):
        """Executes tool calls requested by the agent and returns observations."""
        messages = state["messages"]
        last_message = messages[-1]
        steps = state.get("execution_steps", [])
        
        tool_results = []
        for tool_call in last_message.tool_calls:
            t_name = tool_call["name"]
            t_args = tool_call["args"]
            t_id = tool_call["id"]
            
            steps.append(f"Tool Node: Executing tool '{t_name}'...")
            tool_func = tools_by_name.get(t_name)
            if tool_func:
                res = tool_func.invoke(t_args)
            else:
                res = f"Tool '{t_name}' not found."
                
            tool_results.append(ToolMessage(content=str(res), tool_call_id=t_id))
            steps.append(f"Tool Node: '{t_name}' returned result -> {res}")
            
        return {"messages": tool_results, "execution_steps": steps}

    def should_continue(state: State):
        """Route to tools if the agent requested tool calls, otherwise finish."""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")

    graph = builder.compile()
    return graph, cb
