"""Module 11 — Streaming & Real-time Execution.

Demonstrates token-level streaming from the LLM, collecting partial token
deltas during generation. The node uses `llm.stream()` to emit incremental
tokens and logs each chunk as a stream event.

Graph topology: START → Streaming Node → END
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
    """Streaming state with logs of token events and final assembled output."""
    prompt: str
    stream_logs: List[str]
    final_output: str

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the streaming demonstration graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock streaming simulation.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def streaming_node(state: State):
        """Demonstrate real token streaming via llm.stream() with event logging."""
        prompt = state["prompt"]
        logs = state.get("stream_logs", [])
        logs.append("[Stream Event]: Starting streaming node execution...")

        if llm:
            # Use actual .stream() to demonstrate token-by-token generation
            chunks = []
            token_count = 0
            for chunk in llm.stream([
                SystemMessage(content="You are a streaming demonstrator. Write a 3 sentence paragraph."),
                HumanMessage(content=prompt)
            ]):
                chunk_text = extract_text_content(chunk.content)
                if chunk_text:
                    chunks.append(chunk_text)
                    token_count += 1
                    if token_count <= 5:
                        logs.append(f"[Stream Event]: Received token chunk #{token_count}: '{chunk_text[:30]}...'")
            text = "".join(chunks)
            logs.append(f"[Stream Event]: Finished streaming {token_count} chunks from Anthropic API.")
        else:
            text = f"Token 1... Token 2... Token 3... Streaming complete for prompt: '{prompt}'."
            logs.append("[Stream Event]: Mock streaming simulation complete.")

        return {"final_output": text, "stream_logs": logs}

    builder = StateGraph(State)
    builder.add_node("streaming_node", streaming_node)
    builder.add_edge(START, "streaming_node")
    builder.add_edge("streaming_node", END)

    graph = builder.compile()
    return graph, cb
