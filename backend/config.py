import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    langchain_tracing_v2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "langgraph-mastery-course")
    
    class Config:
        env_file = ".env"

settings = Settings()

# Pricing per 1,000,000 tokens (USD)
# Including model mapping for exact user-specified versions: Haiku 4.5, Sonnet 5, Opus 5
MODEL_PRICING = {
    "claude-5-sonnet": {
        "anthropic_model": "claude-sonnet-5",
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_write": 3.75
    },
    "claude-sonnet-5": {
        "anthropic_model": "claude-sonnet-5",
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_write": 3.75
    },
    "claude-4-5-haiku": {
        "anthropic_model": "claude-haiku-4-5-20251001",
        "input": 0.80,
        "output": 4.00,
        "cache_read": 0.08,
        "cache_write": 1.00
    },
    "claude-haiku-4-5-20251001": {
        "anthropic_model": "claude-haiku-4-5-20251001",
        "input": 0.80,
        "output": 4.00,
        "cache_read": 0.08,
        "cache_write": 1.00
    },
    "claude-5-opus": {
        "anthropic_model": "claude-opus-5",
        "input": 15.00,
        "output": 75.00,
        "cache_read": 1.50,
        "cache_write": 18.75
    },
    "claude-opus-5": {
        "anthropic_model": "claude-opus-5",
        "input": 15.00,
        "output": 75.00,
        "cache_read": 1.50,
        "cache_write": 18.75
    },
    "qwen/qwen3.8-27b": {
        "anthropic_model": "qwen/qwen3.8-27b",
        "input": 0.00,
        "output": 0.00,
        "cache_read": 0.00,
        "cache_write": 0.00
    },
    "llama-3.1-8b-instant": {
        "anthropic_model": "qwen/qwen3.8-27b",
        "input": 0.00,
        "output": 0.00,
        "cache_read": 0.00,
        "cache_write": 0.00
    },
    "gemini-1.5-flash": {
        "anthropic_model": "gemini-1.5-flash",
        "input": 0.00,
        "output": 0.00,
        "cache_read": 0.00,
        "cache_write": 0.00
    }
}

def get_actual_model_string(model_name: str) -> str:
    info = MODEL_PRICING.get(model_name, MODEL_PRICING["claude-sonnet-5"])
    return info["anthropic_model"]

def calculate_cost(input_tokens: int, output_tokens: int, cache_read_tokens: int = 0, cache_write_tokens: int = 0, model_name: str = "claude-sonnet-5") -> float:
    pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["claude-sonnet-5"])
    
    cost = (
        (input_tokens / 1_000_000) * pricing["input"] +
        (output_tokens / 1_000_000) * pricing["output"] +
        (cache_read_tokens / 1_000_000) * pricing["cache_read"] +
        (cache_write_tokens / 1_000_000) * pricing["cache_write"]
    )
    return round(cost, 6)
