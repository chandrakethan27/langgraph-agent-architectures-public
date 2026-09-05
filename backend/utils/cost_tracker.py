from typing import Dict, Any, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from config import calculate_cost

class TokenCostTrackerCallbackHandler(BaseCallbackHandler):
    """Callback handler to track token counts and cost for LLM calls."""
    
    def __init__(self, model_name: str = "claude-sonnet-5"):
        super().__init__()
        self.model_name = model_name
        self.reset()
        
    def reset(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_read_tokens = 0
        self.total_cache_write_tokens = 0
        self.total_cost = 0.0
        self.calls: List[Dict[str, Any]] = []

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if not response.llm_output:
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, "message") and hasattr(gen.message, "usage_metadata"):
                        usage = gen.message.usage_metadata or {}
                        input_t = usage.get("input_tokens", 0)
                        output_t = usage.get("output_tokens", 0)
                        cache_read = usage.get("input_token_details", {}).get("cache_read", 0)
                        cache_write = usage.get("input_token_details", {}).get("cache_creation", 0)
                        
                        call_cost = calculate_cost(input_t, output_t, cache_read, cache_write, self.model_name)
                        
                        self.total_input_tokens += input_t
                        self.total_output_tokens += output_t
                        self.total_cache_read_tokens += cache_read
                        self.total_cache_write_tokens += cache_write
                        self.total_cost += call_cost
                        
                        self.calls.append({
                            "input_tokens": input_t,
                            "output_tokens": output_t,
                            "cache_read_tokens": cache_read,
                            "cache_write_tokens": cache_write,
                            "cost": call_cost,
                            "model": self.model_name
                        })
            return

        token_usage = response.llm_output.get("token_usage", {})
        input_t = token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0))
        output_t = token_usage.get("completion_tokens", token_usage.get("output_tokens", 0))
        cache_read = token_usage.get("cache_read_input_tokens", 0)
        cache_write = token_usage.get("cache_creation_input_tokens", 0)
        
        call_cost = calculate_cost(input_t, output_t, cache_read, cache_write, self.model_name)
        
        self.total_input_tokens += input_t
        self.total_output_tokens += output_t
        self.total_cache_read_tokens += cache_read
        self.total_cache_write_tokens += cache_write
        self.total_cost += call_cost

        self.calls.append({
            "input_tokens": input_t,
            "output_tokens": output_t,
            "cache_read_tokens": cache_read,
            "cache_write_tokens": cache_write,
            "cost": call_cost,
            "model": self.model_name
        })

    def get_summary(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cache_read_tokens": self.total_cache_read_tokens,
            "cache_write_tokens": self.total_cache_write_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "call_count": len(self.calls)
        }
