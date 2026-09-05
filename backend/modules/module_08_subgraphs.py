"""Module 08 — Deep Agents & Sub-Graphs (Nested Graphs).

Demonstrates embedding an entirely compiled sub-graph inside a node of a parent
graph. The sub-agent has its own independent state schema, nodes, and edges.
The parent graph sees it as a single black-box processing step.

Graph topology:
  Parent: START → Preprocess → Invoke Sub-Agent → Format Report → END
  Sub-Agent: Summarize → Extract Entities
"""

from utils.text_helper import extract_text_content
import logging
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

# --- Inner Sub-Agent (Sub-Graph) State ---
class SubAgentState(TypedDict):
    """Independent state schema for the inner sub-agent graph."""
    raw_text: str
    summary: str
    key_entities: List[str]
    sub_steps: List[str]

# --- Parent Agent State ---
class ParentAgentState(TypedDict):
    """Parent graph state that delegates to the sub-agent."""
    user_document: str
    sub_agent_result: dict
    final_presentation: str
    execution_steps: List[str]

def create_subagent_graph(llm):
    """Create a standalone sub-graph agent for text summarization and entity extraction."""

    def summarize_node(state: SubAgentState):
        """Sub-agent node 1: Summarize the input text."""
        text = state["raw_text"]
        steps = state.get("sub_steps", [])
        steps.append("[Sub-Agent] Node 1: Summarizing provided text...")
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="Summarize the input in 2 sentences."),
                HumanMessage(content=text)
            ])
            summary = extract_text_content(res.content)
        else:
            summary = f"Summary of document: {text[:60]}..."

        steps.append("[Sub-Agent] Summary created.")
        return {"summary": summary, "sub_steps": steps}

    def entity_node(state: SubAgentState):
        """Sub-agent node 2: Extract key entities from the input text."""
        text = state["raw_text"]
        steps = state.get("sub_steps", [])
        steps.append("[Sub-Agent] Node 2: Extracting key entities...")
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="Extract top 3 key entities as comma separated words."),
                HumanMessage(content=text)
            ])
            entities = [e.strip() for e in extract_text_content(res.content).split(",")]
        else:
            entities = ["Entity A", "Entity B", "Entity C"]

        steps.append(f"[Sub-Agent] Extracted entities: {entities}")
        return {"key_entities": entities, "sub_steps": steps}

    sub_builder = StateGraph(SubAgentState)
    sub_builder.add_node("summarize_node", summarize_node)
    sub_builder.add_node("entity_node", entity_node)
    
    sub_builder.add_edge(START, "summarize_node")
    sub_builder.add_edge("summarize_node", "entity_node")
    sub_builder.add_edge("entity_node", END)
    
    return sub_builder.compile()

def get_graph(api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
    """Build and compile the parent graph with an embedded sub-agent.

    Args:
        api_key: Anthropic API key. If empty, uses mock fallback responses.
        model_name: Anthropic model identifier.

    Returns:
        Tuple of (compiled parent StateGraph, TokenCostTrackerCallbackHandler).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])
    
    subagent_graph = create_subagent_graph(llm)

    def parent_preprocessor(state: ParentAgentState):
        """Initialize the parent graph and prepare the user document."""
        doc = state["user_document"]
        steps = state.get("execution_steps", [])
        steps.append("Parent Graph: Receiving user document and initializing...")
        return {"execution_steps": steps}

    def invoke_subagent_node(state: ParentAgentState):
        """Delegate processing to the compiled sub-agent graph."""
        doc = state["user_document"]
        steps = state.get("execution_steps", [])
        steps.append("Parent Graph -> Delegating task to Sub-Agent CompiledGraph!")
        
        # Directly invoke the compiled sub-graph as a child execution
        sub_res = subagent_graph.invoke({
            "raw_text": doc,
            "sub_steps": []
        })
        
        steps.extend(sub_res.get("sub_steps", []))
        steps.append("Parent Graph <- Sub-Agent execution completed and returned control!")
        return {"sub_agent_result": sub_res, "execution_steps": steps}

    def parent_formatter(state: ParentAgentState):
        """Format the sub-agent results into an executive presentation."""
        sub_res = state["sub_agent_result"]
        steps = state.get("execution_steps", [])
        steps.append("Parent Graph: Formatting final executive presentation...")

        summary = sub_res.get("summary", "")
        entities = sub_res.get("key_entities", [])
        
        presentation = f"## Executive Analysis Report\n\n**Summary:**\n{summary}\n\n**Key Highlighted Entities:**\n" + "\n".join([f"- {e}" for e in entities])
        steps.append("Parent Graph: Finished workflow.")
        return {"final_presentation": presentation, "execution_steps": steps}

    parent_builder = StateGraph(ParentAgentState)
    parent_builder.add_node("parent_preprocessor", parent_preprocessor)
    parent_builder.add_node("invoke_subagent_node", invoke_subagent_node)
    parent_builder.add_node("parent_formatter", parent_formatter)

    parent_builder.add_edge(START, "parent_preprocessor")
    parent_builder.add_edge("parent_preprocessor", "invoke_subagent_node")
    parent_builder.add_edge("invoke_subagent_node", "parent_formatter")
    parent_builder.add_edge("parent_formatter", END)

    graph = parent_builder.compile()
    return graph, cb
