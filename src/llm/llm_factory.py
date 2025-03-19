from typing import Optional, Dict, Any
import logging
import os

from langchain.llms.base import LLM
from langchain.llms import HuggingFacePipeline, Ollama

from ..config import (
    LLM_MODE,
    LOCAL_MODEL_NAME,
    API_MODEL_NAME,
    OPENAI_API_KEY,
    USE_OLLAMA
)

logger = logging.getLogger(__name__)

def get_llm(
    mode: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> LLM:
    """
    Factory function to get the appropriate LLM.
    
    Args:
        mode: "local" or "api" (defaults to config value)
        model_name: Name of the model to use (defaults to config value)
        **kwargs: Additional arguments to pass to the LLM constructor
    
    Returns:
        An instance of LLM
    """
    mode = mode or LLM_MODE
    
    if mode == "local":
        model_name = model_name or LOCAL_MODEL_NAME
        logger.info(f"Using local LLM: {model_name}")
        
        # If USE_OLLAMA is True, use Ollama
        if USE_OLLAMA:
            return get_ollama_llm(model_name, **kwargs)
        else:
            return get_local_llm(model_name, **kwargs)
    
    elif mode == "api" and OPENAI_API_KEY:
        model_name = model_name or API_MODEL_NAME
        logger.info(f"Using API LLM: {model_name}")
        
        from langchain.chat_models import ChatOpenAI
        
        return ChatOpenAI(
            model_name=model_name,
            openai_api_key=OPENAI_API_KEY,
            temperature=kwargs.get("temperature", 0.9),
            max_tokens=kwargs.get("max_tokens", 2048)
        )
    
    else:
        # Default to Ollama if API mode is selected but no API key is provided
        logger.info(f"Defaulting to Ollama LLM: {LOCAL_MODEL_NAME}")
        return get_ollama_llm(LOCAL_MODEL_NAME, **kwargs)

def get_local_llm(model_name: str, **kwargs) -> LLM:
    """
    Get a local LLM using HuggingFace Transformers.
    
    Args:
        model_name: Name of the model to use
        **kwargs: Additional arguments to pass to the LLM constructor
    
    Returns:
        An instance of LLM
    """
    try:
        # Check if we should use Ollama
        if kwargs.get("use_ollama", False) or USE_OLLAMA:
            return get_ollama_llm(model_name, **kwargs)
        
        # Otherwise use HuggingFace Transformers
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        import torch
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Determine quantization settings
        load_in_8bit = kwargs.get("load_in_8bit", device == "cuda")
        load_in_4bit = kwargs.get("load_in_4bit", False)
        
        model_kwargs = {
            "device_map": "auto",
            "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
        }
        
        if load_in_8bit:
            model_kwargs["load_in_8bit"] = True
        elif load_in_4bit:
            model_kwargs["load_in_4bit"] = True
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs
        )
        
        # Create pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=kwargs.get("max_tokens", 2048),
            temperature=kwargs.get("temperature", 0.1),
            top_p=kwargs.get("top_p", 0.95),
            repetition_penalty=kwargs.get("repetition_penalty", 1.1)
        )
        
        # Create LangChain LLM
        return HuggingFacePipeline(pipeline=pipe)
    
    except Exception as e:
        logger.error(f"Error loading local model {model_name}: {str(e)}")
        raise

def get_ollama_llm(model_name: str, **kwargs) -> LLM:
    """
    Get an LLM using Ollama.
    
    Args:
        model_name: Name of the model to use
        **kwargs: Additional arguments to pass to the LLM constructor
    
    Returns:
        An instance of LLM
    """
    try:
        logger.info(f"Using Ollama LLM: {model_name}")
        
        return Ollama(
            model=model_name,
            temperature=kwargs.get("temperature", 0.1),
            num_ctx=kwargs.get("num_ctx", 4096)
        )
    
    except Exception as e:
        logger.error(f"Error loading Ollama model {model_name}: {str(e)}")
        raise