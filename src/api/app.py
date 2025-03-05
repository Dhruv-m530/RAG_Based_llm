import logging
import os
from typing import List, Optional
from pathlib import Path
import tempfile

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from ..config import DOCUMENTS_DIR
from ..document_processor import DocumentProcessor
from ..rag import RAGChain
from ..vectorstore import get_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Models for API requests and responses
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class DocumentUploadResponse(BaseModel):
    message: str
    document_count: int

class UrlProcessRequest(BaseModel):
    urls: List[HttpUrl]

# Create global instances
document_processor = DocumentProcessor()
rag_chain = RAGChain()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="RAG API",
        description="API for Retrieval-Augmented Generation",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Ensure documents directory exists
    DOCUMENTS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Routes
    @app.post("/query", response_model=QueryResponse)
    async def query(request: QueryRequest):
        """Query the RAG system with a question."""
        try:
            result = rag_chain.query(request.question)
            return result
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/upload", response_model=DocumentUploadResponse)
    async def upload_files(files: List[UploadFile] = File(...)):
        """Upload and process documents."""
        try:
            # Save uploaded files
            file_paths = []
            for file in files:
                # Check file extension
                if not file.filename:
                    continue
                
                ext = Path(file.filename).suffix.lower()
                if ext not in ['.pdf', '.docx', '.doc']:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported file type: {ext}. Only PDF and DOCX files are supported."
                    )
                
                # Save file
                file_path = DOCUMENTS_DIR / file.filename
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                file_paths.append(str(file_path))
            
            # Process documents
            documents = document_processor.process_documents(file_paths)
            
            # Add to vector store
            rag_chain.add_documents(documents)
            
            return {
                "message": f"Successfully processed {len(file_paths)} files",
                "document_count": len(documents)
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/process-urls", response_model=DocumentUploadResponse)
    async def process_urls(request: UrlProcessRequest):
        """Process web URLs."""
        try:
            # Process URLs
            documents = document_processor.process_documents([], urls=[str(url) for url in request.urls])
            
            # Add to vector store
            rag_chain.add_documents(documents)
            
            return {
                "message": f"Successfully processed {len(request.urls)} URLs",
                "document_count": len(documents)
            }
        
        except Exception as e:
            logger.error(f"Error processing URLs: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app