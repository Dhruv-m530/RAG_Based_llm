from typing import List, Dict, Any, Optional
import logging

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain.llms.base import LLM

from ..config import TOP_K_RETRIEVAL
from ..llm import get_llm
from ..vectorstore import get_vector_store

logger = logging.getLogger(__name__)

class RAGChain:
    """Main RAG chain that combines retrieval and generation."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        llm: Optional[LLM] = None,
        top_k: int = TOP_K_RETRIEVAL
    ):
        """
        Initialize the RAG chain.
        
        Args:
            vector_store: Vector store for retrieval
            llm: Language model for generation
            top_k: Number of documents to retrieve
        """
        self.vector_store = vector_store or get_vector_store()
        self.llm = llm or get_llm()
        self.top_k = top_k
        
        # Create the retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.top_k}
        )
        
        # Create the chain
        self.chain = self._create_chain()
    
    def _create_chain(self) -> RetrievalQA:
        """Create the retrieval QA chain."""
        # Define the prompt template
        template = """
        You are a helpful assistant that answers questions based on the provided context.
        
        Context:
        {context}
        
        Question:
        {question}
        
        Instructions:
        - Answer the question based on the context provided.
        - If the context doesn't contain the answer, then search on google or web if not found then say "I don't have enough information to answer this question."
        - Provide detailed and accurate answers.
        - Cite specific parts of the context when relevant.
        
        Answer:
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create the chain
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG chain.
        
        Args:
            question: Question to answer
        
        Returns:
            Dictionary with answer and source documents
        """
        logger.info(f"Querying RAG chain with question: {question}")
        
        try:
            result = self.chain({"query": question})
            
            # Format the result
            answer = result.get("result", "")
            source_documents = result.get("source_documents", [])
            
            # Extract source information
            sources = []
            for doc in source_documents:
                source = {
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source)
            
            return {
                "answer": answer,
                "sources": sources
            }
        
        except Exception as e:
            logger.error(f"Error querying RAG chain: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: Documents to add
        """
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        try:
            self.vector_store.add_documents(documents)
            
            # Update the retriever
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k}
            )
            
            # Recreate the chain
            self.chain = self._create_chain()
            
            logger.info("Documents added successfully")
        
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise