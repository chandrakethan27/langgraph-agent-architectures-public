"""LangGraph Mastery Educational Platform — FastAPI Backend.

Provides REST endpoints for executing 14 LangGraph agent architecture modules,
each demonstrating a distinct agent design pattern (routing, ReAct, HITL,
multi-agent, reflection, map-reduce, etc.).
"""

from langsmith import Client
from langchain_core.tracers.langchain import LangChainTracer
from utils.text_helper import extract_text_content
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Dict, Any, List, Optional
import logging
import os
from config import get_actual_model_string

logger = logging.getLogger(__name__)

from modules import (
    module_01_basics,
    module_02_routing,
    module_03_react,
    module_03b_plan_execute,
    module_04_memory,
    module_05_hitl,
    module_06_timetravel,
    module_07_multi_agent,
    module_08_subgraphs,
    module_09_reflection,
    module_09b_map_reduce,
    module_10_eval_langsmith,
    module_11_streaming,
    module_12_context,
)

app = FastAPI(title="LangGraph Mastery Educational Platform", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODULE_REGISTRY = {
    "module_01": {
        "id": "module_01",
        "title": "1. Fundamentals: State, Nodes & Edges",
        "description": "Learn how StateGraph manages data flow across sequential nodes.",
        "mermaid": "graph TD\\n  START([START]) --> generate_outline[Generate Outline]\\n  generate_outline --> write_content[Write Content]\\n  write_content --> END([END])"
    },
    "module_02": {
        "id": "module_02",
        "title": "2. Decision Making: Conditional Edges (Routing)",
        "description": "Dynamic graph routing based on intent classification.",
        "mermaid": "graph TD\\n  START([START]) --> classify[Classify Intent]\\n  classify -->|math| math_node[Math Expert]\\n  classify -->|code| code_node[Code Expert]\\n  classify -->|general| general_node[General Assistant]\\n  math_node --> END([END])\\n  code_node --> END([END])\\n  general_node --> END([END])"
    },
    "module_03": {
        "id": "module_03",
        "title": "3. ReAct Agent: Tool Calling Loop",
        "description": "Classic agentic reasoning and tool execution loop.",
        "mermaid": "graph TD\\n  START([START]) --> agent[Agent Node]\\n  agent -->|has tool_calls| tools[Tool Node]\\n  tools --> agent\\n  agent -->|final answer| END([END])"
    },
    "module_03b": {
        "id": "module_03b",
        "title": "3b. Plan-and-Execute Agent",
        "description": "Separating high-level planning from step-by-step task execution.",
        "mermaid": "graph TD\\n  START([START]) --> planner[Planner Node]\\n  planner --> executor[Executor Node]\\n  executor --> replanner[Replanner Node]\\n  replanner -->|more steps| executor\\n  replanner -->|finished| END([END])"
    },
    "module_04": {
        "id": "module_04",
        "title": "4. Memory: Short-Term vs. Long-Term",
        "description": "Session thread checkpointing vs. cross-thread persistent Store API.",
        "mermaid": "graph TD\\n  START([START]) --> fetch_mem[\"Fetch Long-Term Memory\"]\\n  fetch_mem --> chat[\"Chat Node + Thread Checkpointer\"]\\n  chat --> END([END])"
    },
    "module_05": {
        "id": "module_05",
        "title": "5. Guardrails & Human-in-the-Loop",
        "description": "Using interrupt_before to halt graph execution for human authorization.",
        "mermaid": "graph TD\\n  START([START]) --> propose[Propose Action]\\n  propose -. INTERRUPT .-> dangerous[Dangerous Action Node]\\n  dangerous --> END([END])"
    },
    "module_06": {
        "id": "module_06",
        "title": "6. Time Travel & State Rewinding",
        "description": "Inspecting checkpoint history and branching execution from past states.",
        "mermaid": "graph TD\\n  START([START]) --> step1[\"Step 1 (Checkpt 1)\"]\\n  step1 --> step2[\"Step 2 (Checkpt 2)\"]\\n  step2 --> step3[\"Step 3 (Checkpt 3)\"]\\n  step3 --> END([END])"
    },
    "module_07": {
        "id": "module_07",
        "title": "7. Multi-Agent Supervisor Architecture",
        "description": "Orchestrating multiple specialized worker agents via a central supervisor.",
        "mermaid": "graph TD\\n  START([START]) --> supervisor[Supervisor Agent]\\n  supervisor -->|delegate| researcher[Researcher Agent]\\n  supervisor -->|delegate| coder[Coder Agent]\\n  researcher --> supervisor\\n  coder --> supervisor\\n  supervisor -->|FINISH| END([END])"
    },
    "module_08": {
        "id": "module_08",
        "title": "8. Deep Agents & Sub-Graphs (Nested Graphs)",
        "description": "Embedding an entirely compiled sub-graph inside a node of a parent graph.",
        "mermaid": "graph TD\\n  subgraph parent[\"Parent Graph\"]\\n    START([START]) --> pre[Preprocess]\\n    pre --> subnode[\"Invoke Sub-Agent Node\"]\\n    subnode --> fmt[Format Report]\\n    fmt --> END([END])\\n  end\\n  subgraph inner[\"Inner Sub-Agent Graph\"]\\n    summarize --> entity\\n  end"
    },
    "module_09": {
        "id": "module_09",
        "title": "9. Reflection & Self-Correction",
        "description": "Generator-Evaluator loop for iterative critique and refinement.",
        "mermaid": "graph TD\\n  START([START]) --> generator[Generator Node]\\n  generator --> evaluator[Evaluator Node]\\n  evaluator -->|rejected| generator\\n  evaluator -->|passed| END([END])"
    },
    "module_09b": {
        "id": "module_09b",
        "title": "9b. Map-Reduce (Parallel Execution)",
        "description": "Fanning out tasks to parallel worker nodes and reducing into a final summary.",
        "mermaid": "graph TD\\n  START([START]) --> fanout[Fan-Out Node]\\n  fanout --> worker1[Worker Node 1]\\n  fanout --> worker2[Worker Node 2]\\n  fanout --> worker3[Worker Node 3]\\n  worker1 --> reduce[Reduce Node]\\n  worker2 --> reduce\\n  worker3 --> reduce\\n  reduce --> END([END])"
    },
    "module_10": {
        "id": "module_10",
        "title": "10. Observability & Evaluation (LangSmith)",
        "description": "LLM-as-a-judge dataset evaluation and execution tracing.",
        "mermaid": "graph TD\\n  START([START]) --> dataset[Load Dataset]\\n  dataset --> eval[\"LLM Judge Evaluation\"]\\n  eval --> metrics[\"Aggregate Accuracy & Cost Metrics\"]\\n  metrics --> END([END])"
    },
    "module_11": {
        "id": "module_11",
        "title": "11. Streaming & Real-time Execution",
        "description": "Token streaming vs state chunk streaming.",
        "mermaid": "graph TD\\n  START([START]) --> stream_node[Streaming Node]\\n  stream_node --> END([END])"
    },
    "module_12": {
        "id": "module_12",
        "title": "12. Context & Dependency Injection",
        "description": "Injecting RunnableConfig without modifying state schemas.",
        "mermaid": "graph TD\\n  START([START]) --> context_node[\"Context-Aware Node (Injected Config)\"]\\n  context_node --> END([END])"
    }
}

class RunModuleRequest(BaseModel):
    """Request schema for executing a LangGraph agent module."""
    module_id: str
    input_text: str
    api_key: Optional[str] = ""
    langsmith_key: Optional[str] = ""
    model_name: Optional[str] = "claude-sonnet-5"
    thread_id: Optional[str] = "thread_1"
    user_id: Optional[str] = "user_demo"
    is_approved: Optional[bool] = False

    @field_validator("input_text")
    @classmethod
    def validate_input_length(cls, v: str) -> str:
        max_len = 10_000
        if len(v) > max_len:
            raise ValueError(f"input_text exceeds maximum length of {max_len} characters")
        return v

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "LangGraph Mastery Platform Backend"}

@app.get("/api/modules")
def get_modules():
    return list(MODULE_REGISTRY.values())

@app.post("/api/run_module")
def run_module(req: RunModuleRequest):
    mod_id = req.module_id
    if mod_id not in MODULE_REGISTRY:
        raise HTTPException(status_code=404, detail="Module not found")
        
    api_key = req.api_key.strip() if req.api_key else os.getenv("ANTHROPIC_API_KEY", "")
    model_name = req.model_name.strip() if req.model_name else "claude-5-sonnet"
    actual_model = get_actual_model_string(model_name)

    # Build LangSmith config for RunnableConfig injection (thread-safe, no os.environ mutation)
    langsmith_key = req.langsmith_key.strip() if req.langsmith_key else os.getenv("LANGCHAIN_API_KEY", "")
    langsmith_config = {}
    if langsmith_key:
        try:
            ls_client = Client(api_key=langsmith_key)
            tracer = LangChainTracer(project_name="langgraph-agent-architectures", client=ls_client)
            langsmith_config = {
                "callbacks": [tracer],
            }
        except Exception as e:
            logger.error("Failed to initialize LangSmith tracer: %s", e)
        logger.info("LangSmith tracing enabled for module=%s", mod_id)

    try:
        if mod_id == "module_01":
            graph, cb = module_01_basics.get_graph(api_key, actual_model)
            result = graph.invoke({"topic": req.input_text, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_02":
            graph, cb = module_02_routing.get_graph(api_key, actual_model)
            result = graph.invoke({"input_prompt": req.input_text, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_03":
            graph, cb = module_03_react.get_graph(api_key, actual_model)
            from langchain_core.messages import HumanMessage
            result = graph.invoke({"messages": [HumanMessage(content=req.input_text)], "execution_steps": [], "iteration_count": 0})
            msgs = [{"type": m.type, "content": extract_text_content(m.content), "tool_calls": getattr(m, "tool_calls", [])} for m in result["messages"]]
            result["messages"] = msgs
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_03b":
            graph, cb = module_03b_plan_execute.get_graph(api_key, actual_model)
            result = graph.invoke({"input_query": req.input_text, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_04":
            graph, cb = module_04_memory.get_graph(api_key, actual_model)
            from langchain_core.messages import HumanMessage
            config = {"configurable": {"thread_id": req.thread_id}}
            result = graph.invoke({"messages": [HumanMessage(content=req.input_text)], "user_id": req.user_id, "execution_steps": []}, config=config)
            msgs = [{"type": m.type, "content": extract_text_content(m.content)} for m in result["messages"]]
            result["messages"] = msgs
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_05":
            graph, cb = module_05_hitl.get_graph(api_key, actual_model)
            config = {"configurable": {"thread_id": req.thread_id}}
            graph.invoke({"proposed_action": req.input_text, "is_approved": req.is_approved, "execution_steps": []}, config=config)
            state_snapshot = graph.get_state(config)
            
            if state_snapshot.next:
                return {
                    "result": {
                        "proposed_action": req.input_text,
                        "status": "INTERRUPTED",
                        "next_node": state_snapshot.next,
                        "execution_steps": state_snapshot.values.get("execution_steps", [])
                    },
                    "metrics": cb.get_summary(),
                    "requires_approval": True
                }
            else:
                return {"result": state_snapshot.values, "metrics": cb.get_summary(), "requires_approval": False}

        elif mod_id == "module_06":
            graph, cb = module_06_timetravel.get_graph(api_key, actual_model)
            config = {"configurable": {"thread_id": req.thread_id}}
            result = graph.invoke({"data": req.input_text, "step_count": 0, "execution_steps": []}, config=config)
            
            history = []
            for state in graph.get_state_history(config):
                history.append({
                    "checkpoint_id": state.config["configurable"]["checkpoint_id"],
                    "node": state.next,
                    "values": state.values
                })
            result["history"] = history
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_07":
            graph, cb = module_07_multi_agent.get_graph(api_key, actual_model)
            result = graph.invoke({"task": req.input_text, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_08":
            graph, cb = module_08_subgraphs.get_graph(api_key, actual_model)
            result = graph.invoke({"user_document": req.input_text, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_09":
            graph, cb = module_09_reflection.get_graph(api_key, actual_model)
            result = graph.invoke({"prompt": req.input_text, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_09b":
            graph, cb = module_09b_map_reduce.get_graph(api_key, actual_model)
            chunks = [c.strip() for c in req.input_text.split(";") if c.strip()]
            if not chunks:
                chunks = ["Chunk A: Basics of AI", "Chunk B: Neural Networks", "Chunk C: Agentic Workflows"]
            result = graph.invoke({"input_chunks": chunks, "execution_steps": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_10":
            eval_results, metrics = module_10_eval_langsmith.run_evaluation(api_key, actual_model)
            return {"result": {"evaluation_suite": eval_results}, "metrics": metrics}

        elif mod_id == "module_11":
            graph, cb = module_11_streaming.get_graph(api_key, actual_model)
            result = graph.invoke({"prompt": req.input_text, "stream_logs": []})
            return {"result": result, "metrics": cb.get_summary()}

        elif mod_id == "module_12":
            graph, cb = module_12_context.get_graph(api_key, actual_model)
            config = {
                "configurable": {
                    "tenant_id": "enterprise-org-99",
                    "database_url": "<injected-at-runtime>",
                    "experimental_feature": True
                }
            }
            result = graph.invoke({"input_text": req.input_text, "execution_steps": []}, config=config)
            return {"result": result, "metrics": cb.get_summary()}

    except Exception as e:
        logger.exception("Module %s execution failed", mod_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approve_hitl")
def approve_hitl(req: RunModuleRequest):
    """Resume a Human-in-the-Loop graph after human approval/rejection."""
    api_key = req.api_key.strip() if req.api_key else os.getenv("ANTHROPIC_API_KEY", "")
    model_name = req.model_name.strip() if req.model_name else "claude-5-sonnet"
    actual_model = get_actual_model_string(model_name)

    try:
        graph, cb = module_05_hitl.get_graph(api_key, actual_model)
        config = {"configurable": {"thread_id": req.thread_id}}

        graph.update_state(config, {"is_approved": req.is_approved}, as_node="propose_action_node")
        final_res = graph.invoke(None, config=config)

        return {"result": final_res, "metrics": cb.get_summary()}
    except Exception as e:
        logger.exception("HITL approval failed")
        raise HTTPException(status_code=500, detail=str(e))
