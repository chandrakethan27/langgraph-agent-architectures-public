"""Module 04 — Memory: Short-Term vs. Long-Term.

Demonstrates dual memory architecture combining thread-scoped short-term memory
(via LangGraph's MemorySaver checkpointer) with cross-thread long-term memory
(via an in-memory user fact store with thread-safe access).

Graph topology: START → Fetch Long-Term Memory → Chat Node → END
"""

from utils.text_helper import extract_text_content
import logging
import threading
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from cachetools import LRUCache
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from utils.llm_factory import get_llm
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

# Thread-safe in-memory store for cross-thread long-term user facts.
# Protected by _user_stores_lock to prevent race conditions under concurrent requests.
_user_stores_lock = threading.Lock()
USER_STORES = LRUCache(maxsize=1000)

# Shared SQLite checkpointer to persist checkpoints across HTTP requests and prevent RAM OOM
_conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
shared_checkpointer = SqliteSaver(_conn)
shared_checkpointer.setup()

class State(TypedDict):
    """Memory agent state combining message history with user-level facts."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    user_facts: List[str]
    execution_steps: List[str]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the memory agent graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback responses.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])
    checkpointer = shared_checkpointer

    def fetch_long_term_memory(state: State):
        """Retrieve stored cross-thread facts for the current user."""
        user_id = state.get("user_id", "default_user")
        steps = state.get("execution_steps", [])
        steps.append(f"Long-term Memory Node: Fetching stored facts for user_id='{user_id}'...")

        with _user_stores_lock:
            stored_facts = list(USER_STORES.get(user_id, []))

        steps.append(f"Long-term Memory Node: Found {len(stored_facts)} cross-thread facts.")
        return {"user_facts": stored_facts, "execution_steps": steps}

    def chat_node(state: State):
        """Generate a response using both short-term (thread) and long-term (user store) memory."""
        messages = state["messages"]
        user_facts = state.get("user_facts", [])
        user_id = state.get("user_id", "default_user")
        steps = state.get("execution_steps", [])
        steps.append("Chat Node: Generating response using Short-term (Thread) and Long-term Memory...")

        system_prompt = "You are a helpful assistant with memory."
        if user_facts:
            system_prompt += f"\nKnown long-term facts about this user ({user_id}):\n" + "\n".join([f"- {f}" for f in user_facts])

        if llm:
            sys_msg = SystemMessage(content=system_prompt)
            res = llm.invoke([sys_msg] + messages)
            reply = extract_text_content(res.content)
        else:
            last_human = [m for m in messages if isinstance(m, HumanMessage)][-1].content
            reply = f"I remembered your conversation in this thread (Short-term)! Also from Long-term memory for user '{user_id}': {user_facts or 'No prior facts'}. Your message was: '{last_human}'"

        # Check if user mentioned a new fact to save long-term
        last_msg_str = extract_text_content(messages[-1].content) if messages else ""
        if "my name is" in last_msg_str.lower() or "i like" in last_msg_str.lower() or "i work as" in last_msg_str.lower():
            with _user_stores_lock:
                if user_id not in USER_STORES:
                    USER_STORES[user_id] = []
                USER_STORES[user_id].append(last_msg_str)
            logger.info("Saved long-term fact for user '%s'", user_id)
            steps.append(f"Long-term Memory Node: Saved new cross-thread fact: '{last_msg_str}' for user '{user_id}'")

        steps.append("Chat Node: Response generated.")
        return {"messages": [AIMessage(content=reply)], "execution_steps": steps}

    builder = StateGraph(State)
    builder.add_node("fetch_long_term_memory", fetch_long_term_memory)
    builder.add_node("chat_node", chat_node)

    builder.add_edge(START, "fetch_long_term_memory")
    builder.add_edge("fetch_long_term_memory", "chat_node")
    builder.add_edge("chat_node", END)

    graph = builder.compile(checkpointer=checkpointer)
    return graph, cb
