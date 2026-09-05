import logging
from typing import Optional, List
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)

def get_llm(model_name: str, api_key: str, callbacks: Optional[List[BaseCallbackHandler]] = None):
    """
    Factory function to instantiate the correct LLM class based on the model name.
    
    Args:
        model_name: The name of the model (e.g., 'claude-5-sonnet', 'llama-3.1-8b-instant', 'gemini-1.5-flash').
        api_key: The API key for the respective provider.
        callbacks: Optional list of callbacks for tracing/cost tracking.
        
    Returns:
        A LangChain Chat model instance, or None if api_key is missing.
    """
    if not api_key:
        return None
        
    callbacks = callbacks or []
    
    if "claude" in model_name.lower():
        return ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            callbacks=callbacks
        )
    elif "llama" in model_name.lower() or "mixtral" in model_name.lower() or "gemma" in model_name.lower() or "qwen" in model_name.lower():
        # Groq models
        return ChatGroq(
            model=model_name,
            groq_api_key=api_key,
            callbacks=callbacks
        )
    elif "gemini" in model_name.lower():
        # Google Gemini models
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            callbacks=callbacks
        )
    else:
        logger.warning(f"Unknown model provider for {model_name}. Inferring from API key...")
        if api_key.startswith("gsk_"):
            return ChatGroq(model=model_name, groq_api_key=api_key, callbacks=callbacks)
        elif api_key.startswith("AIza"):
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, callbacks=callbacks)
        else:
            return ChatAnthropic(model=model_name, anthropic_api_key=api_key, callbacks=callbacks)
