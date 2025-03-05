from typing import Optional
import logging

from langchain.embeddings.base import Embeddings
from langchain.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings  # Ollama has moved to a separate package

from ..config import (
    EMBEDDING_MODE, 
    LOCAL_EMBEDDING_MODEL, 
    API_EMBEDDING_MODEL,
    OPENAI_API_KEY,
    USE_OLLAMA
)

logger = logging.getLogger(__name__)

def get_embeddings(
    mode: Optional[str] = None, 
    model_name: Optional[str] = None
) -> Embeddings:
    """
    Factory function to get the appropriate embeddings model.
    
    Args:
        mode: "local" or "api" (defaults to config value)
        model_name: Name of the model to use (defaults to config value)
    
    Returns:
        An instance of Embeddings
    """
    mode = mode or EMBEDDING_MODE
    
    # If USE_OLLAMA is True, try to use Ollama for embeddings
    if USE_OLLAMA and mode == "local":
        try:
            logger.info("Attempting to use Ollama for embeddings")
            return OllamaEmbeddings(model="nomic-embed-text")
        except Exception as e:
            logger.warning(f"Failed to use Ollama for embeddings: {str(e)}. Falling back to HuggingFace.")
    
    if mode == "local":
        model_name = model_name or LOCAL_EMBEDDING_MODEL
        logger.info(f"Using local embeddings model: {model_name}")
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cuda" if is_cuda_available() else "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    
    elif mode == "api" and OPENAI_API_KEY:
        model_name = model_name or API_EMBEDDING_MODEL
        logger.info(f"Using API embeddings model: {model_name}")
        
        from langchain.embeddings import OpenAIEmbeddings
        
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=OPENAI_API_KEY
        )
    
    else:
        # Default to HuggingFace embeddings
        model_name = model_name or LOCAL_EMBEDDING_MODEL
        logger.info(f"Defaulting to local embeddings model: {model_name}")
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cuda" if is_cuda_available() else "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

def is_cuda_available() -> bool:
    """Check if CUDA is available for GPU acceleration."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False




# from typing import Optional
# import logging

# from langchain.embeddings.base import Embeddings
# from langchain.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings

# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_ollama import OllamaEmbeddings  # Ollama has moved to a separate package

# from ..config import (
#     EMBEDDING_MODE, 
#     LOCAL_EMBEDDING_MODEL, 
#     API_EMBEDDING_MODEL,
#     OPENAI_API_KEY,
#     USE_OLLAMA
# )

# logger = logging.getLogger(__name__)

# def get_embeddings(
#     mode: Optional[str] = None, 
#     model_name: Optional[str] = None
# ) -> Embeddings:
#     """
#     Factory function to get the appropriate embeddings model.
    
#     Args:
#         mode: "local" or "api" (defaults to config value)
#         model_name: Name of the model to use (defaults to config value)
    
#     Returns:
#         An instance of Embeddings
#     """
#     mode = mode or EMBEDDING_MODE
    
#     # If USE_OLLAMA is True, try to use Ollama for embeddings
#     if USE_OLLAMA and mode == "local":
#         try:
#             logger.info("Attempting to use Ollama for embeddings")
#             return OllamaEmbeddings(model="nomic-embed-text")
#         except Exception as e:
#             logger.warning(f"Failed to use Ollama for embeddings: {str(e)}. Falling back to HuggingFace.")
    
#     if mode == "local":
#         model_name = model_name or LOCAL_EMBEDDING_MODEL
#         logger.info(f"Using local embeddings model: {model_name}")
        
#         return HuggingFaceEmbeddings(
#             model_name=model_name,
#             model_kwargs={"device": "cuda" if is_cuda_available() else "cpu"},
#             encode_kwargs={"normalize_embeddings": True}
#         )
    
#     elif mode == "api" and OPENAI_API_KEY:
#         model_name = model_name or API_EMBEDDING_MODEL
#         logger.info(f"Using API embeddings model: {model_name}")
        
#         from langchain.embeddings import OpenAIEmbeddings
        
#         return OpenAIEmbeddings(
#             model=model_name,
#             openai_api_key=OPENAI_API_KEY
#         )
    
#     else:
#         # Default to HuggingFace embeddings
#         model_name = model_name or LOCAL_EMBEDDING_MODEL
#         logger.info(f"Defaulting to local embeddings model: {model_name}")
        
#         return HuggingFaceEmbeddings(
#             model_name=model_name,
#             model_kwargs={"device": "cuda" if is_cuda_available() else "cpu"},
#             encode_kwargs={"normalize_embeddings": True}
#         )

# def is_cuda_available() -> bool:
#     """Check if CUDA is available for GPU acceleration."""
#     try:
#         import torch
#         return torch.cuda.is_available()
#     except ImportError:
#         return False