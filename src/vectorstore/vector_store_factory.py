from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.embeddings import Embeddings  # Updated import


from langchain.schema import Document
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings.base import Embeddings

from ..config import VECTOR_DB_PATH
from ..embeddings import get_embeddings

logger = logging.getLogger(__name__)

def get_vector_store(
    store_type: str = "faiss",
    embedding_model: Optional[Embeddings] = None,
    persist_directory: Optional[str] = None,
    documents: Optional[List[Document]] = None
):
    """
    Factory function to get the appropriate vector store.
    
    Args:
        store_type: "faiss" or "chroma"
        embedding_model: Embeddings model to use
        persist_directory: Directory to persist the vector store
        documents: Documents to add to the vector store
    
    Returns:
        An instance of a vector store
    """
    # Get embeddings if not provided
    embedding_model = embedding_model or get_embeddings()
    
    # Get persist directory if not provided
    persist_directory = persist_directory or VECTOR_DB_PATH
    Path(persist_directory).mkdir(exist_ok=True, parents=True)
    
    if store_type.lower() == "faiss":
        return get_faiss_store(embedding_model, persist_directory, documents)
    elif store_type.lower() == "chroma":
        return get_chroma_store(embedding_model, persist_directory, documents)
    else:
        raise ValueError(f"Invalid vector store type: {store_type}")


def get_faiss_store(
    embedding_model: Embeddings,
    persist_directory: str,
    documents: Optional[List[Document]] = None
):
    """Get a FAISS vector store."""
    persist_path = Path(persist_directory) / "faiss"
    persist_path.mkdir(exist_ok=True, parents=True)

    if documents:
        logger.info(f"Creating new FAISS index with {len(documents)} documents")
        vector_store = FAISS.from_documents(documents, embedding_model)
        vector_store.save_local(str(persist_path))
        return vector_store
    else:
        try:
            logger.info(f"Loading existing FAISS index from {persist_path}")
            return FAISS.load_local(
                str(persist_path), embedding_model, allow_dangerous_deserialization=True
            )
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {str(e)}")
            logger.info("Creating empty FAISS index")
            # Fix: Ensure at least one dummy document
            vector_store = FAISS.from_texts(["dummy"], embedding_model)
            vector_store.save_local(str(persist_path))
            return vector_store
 
def get_chroma_store(
    embedding_model: Embeddings,
    persist_directory: str,
    documents: Optional[List[Document]] = None
):
    """Get a Chroma vector store."""
    persist_path = Path(persist_directory) / "chroma"
    persist_path.mkdir(exist_ok=True, parents=True)
    
    if documents:
        logger.info(f"Creating/updating Chroma DB with {len(documents)} documents")
        return Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=str(persist_path)
        )
    else:
        try:
            logger.info(f"Loading existing Chroma DB from {persist_path}")
            return Chroma(
                embedding_function=embedding_model,
                persist_directory=str(persist_path)
            )
        except Exception as e:
            logger.warning(f"Could not load Chroma DB: {str(e)}")
            logger.info("Creating empty Chroma DB")
            vector_store = Chroma(
                embedding_function=embedding_model,
                persist_directory=str(persist_path)
            )
            return vector_store