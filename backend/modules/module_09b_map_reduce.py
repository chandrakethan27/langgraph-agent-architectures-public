"""Module 09b — Map-Reduce (Parallel Execution).

Demonstrates LangGraph's parallel execution by fanning out work to concurrent
worker nodes and then reducing (aggregating) all results into a unified summary.
Uses `Annotated[List[str], operator.add]` for thread-safe state merging.

Graph topology: START → Fan-Out → {Worker1 || Worker2 || Worker3} → Reduce → END
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

class State(TypedDict):
    """Map-reduce state with input chunks, per-chunk summaries, and final reduction."""
    input_chunks: List[str]
    chunk_1_summary: str
    chunk_2_summary: str
    chunk_3_summary: str
    final_reduction: str
    execution_steps: Annotated[List[str], operator.add]

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the map-reduce parallel execution graph.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback summaries.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])

    def fan_out_node(state: State):
        """Receive input chunks and prepare for parallel distribution."""
        chunks = state.get("input_chunks", ["Chunk A: Basics of AI", "Chunk B: Neural Networks", "Chunk C: Agentic Workflows"])
        return {
            "input_chunks": chunks,
            "execution_steps": [f"Fan-Out Node: Received {len(chunks)} chunks. Fanning out to parallel worker nodes..."]
        }

    def process_chunk_1(state: State):
        """Parallel worker 1: Process and summarize the first chunk."""
        chunks = state["input_chunks"]
        c1 = chunks[0] if len(chunks) > 0 else "Default Chunk 1"
        
        if llm:
            res = llm.invoke([SystemMessage(content="Summarize in 1 sentence."), HumanMessage(content=c1)])
            s1 = extract_text_content(res.content)
        else:
            s1 = f"Summary of {c1}"

        return {
            "chunk_1_summary": s1,
            "execution_steps": [f"[Parallel Worker 1]: Processed '{c1}'"]
        }

    def process_chunk_2(state: State):
        """Parallel worker 2: Process and summarize the second chunk."""
        chunks = state["input_chunks"]
        c2 = chunks[1] if len(chunks) > 1 else "Default Chunk 2"

        if llm:
            res = llm.invoke([SystemMessage(content="Summarize in 1 sentence."), HumanMessage(content=c2)])
            s2 = extract_text_content(res.content)
        else:
            s2 = f"Summary of {c2}"

        return {
            "chunk_2_summary": s2,
            "execution_steps": [f"[Parallel Worker 2]: Processed '{c2}'"]
        }

    def process_chunk_3(state: State):
        """Parallel worker 3: Process and summarize the third chunk."""
        chunks = state["input_chunks"]
        c3 = chunks[2] if len(chunks) > 2 else "Default Chunk 3"

        if llm:
            res = llm.invoke([SystemMessage(content="Summarize in 1 sentence."), HumanMessage(content=c3)])
            s3 = extract_text_content(res.content)
        else:
            s3 = f"Summary of {c3}"

        return {
            "chunk_3_summary": s3,
            "execution_steps": [f"[Parallel Worker 3]: Processed '{c3}'"]
        }

    def reduce_node(state: State):
        """Aggregate all parallel worker summaries into a unified synthesis."""
        s1 = state.get("chunk_1_summary", "")
        s2 = state.get("chunk_2_summary", "")
        s3 = state.get("chunk_3_summary", "")

        combined = f"### Consolidated Map-Reduce Output\n\n1. {s1}\n2. {s2}\n3. {s3}"
        return {
            "final_reduction": combined,
            "execution_steps": [
                "Reduce Node: Aggregated all parallel summaries into a final synthesis.",
                "Map-Reduce Workflow Completed!"
            ]
        }

    builder = StateGraph(State)
    builder.add_node("fan_out", fan_out_node)
    builder.add_node("process_chunk_1", process_chunk_1)
    builder.add_node("process_chunk_2", process_chunk_2)
    builder.add_node("process_chunk_3", process_chunk_3)
    builder.add_node("reduce", reduce_node)

    builder.add_edge(START, "fan_out")
    
    # Parallel edges from fan_out to workers
    builder.add_edge("fan_out", "process_chunk_1")
    builder.add_edge("fan_out", "process_chunk_2")
    builder.add_edge("fan_out", "process_chunk_3")

    # All workers connect into the reduce node
    builder.add_edge("process_chunk_1", "reduce")
    builder.add_edge("process_chunk_2", "reduce")
    builder.add_edge("process_chunk_3", "reduce")

    builder.add_edge("reduce", END)

    graph = builder.compile()
    return graph, cb
