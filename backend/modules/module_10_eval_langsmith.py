"""Module 10 — Observability & Evaluation (LangSmith).

Implements an automated LLM-as-a-Judge evaluation pipeline. An impartial LLM
scores agent outputs against benchmark test datasets, grading accuracy from
0-100 and providing diagnostic feedback for each sample.
"""

from utils.text_helper import extract_text_content
import logging
import os
from typing import TypedDict, List, Dict, Any
from utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from utils.cost_tracker import TokenCostTrackerCallbackHandler

logger = logging.getLogger(__name__)

def run_evaluation(api_key: str, model_name: str = "claude-haiku-4-5-20251001", dataset_samples: List[Dict[str, str]] = None):
    """Run LLM-as-a-Judge evaluation against a benchmark dataset.

    Args:
        api_key: Anthropic API key. If empty, uses deterministic mock scoring.
        model_name: Anthropic model identifier.
        dataset_samples: List of dicts with 'input', 'expected', 'agent_output' keys.

    Returns:
        Tuple of (evaluation results list, token cost summary dict).
    """
    cb = TokenCostTrackerCallbackHandler(model_name=model_name)
    llm = get_llm(model_name, api_key, callbacks=[cb])
    
    if not dataset_samples:
        dataset_samples = [
            {"input": "What is 15 * 12?", "expected": "180", "agent_output": "15 * 12 is equal to 180."},
            {"input": "Who wrote Hamlet?", "expected": "William Shakespeare", "agent_output": "Hamlet was written by William Shakespeare in the early 1600s."},
            {"input": "What is the capital of France?", "expected": "Paris", "agent_output": "The capital of France is Berlin."} # Intentional error for testing eval
        ]

    eval_results = []
    
    for sample in dataset_samples:
        inp = sample["input"]
        exp = sample["expected"]
        out = sample["agent_output"]
        
        if llm:
            res = llm.invoke([
                SystemMessage(content="You are an LLM Judge evaluating AI Agent responses. Grade accuracy on a scale of 0 to 100. Format response strictly as JSON: {\"score\": <int>, \"reason\": \"<string>\"}"),
                HumanMessage(content=f"Input: {inp}\nExpected: {exp}\nAgent Response: {out}")
            ])
            eval_text = extract_text_content(res.content)
        else:
            if "berlin" in out.lower() and "france" in inp.lower():
                eval_text = '{"score": 0, "reason": "Incorrect capital city provided. Capital of France is Paris, not Berlin."}'
            else:
                eval_text = '{"score": 100, "reason": "Response accurately matches expected answer."}'

        eval_results.append({
            "sample": sample,
            "evaluation": eval_text
        })
        
    return eval_results, cb.get_summary()
