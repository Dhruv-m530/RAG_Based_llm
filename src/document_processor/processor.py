import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_community.document_loaders import WebBaseLoader

from .loaders import PDFLoader, DocxLoader, WebLoader, TxtLoader
from ..config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing class that handles different document types."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.web_loader = WebBaseLoader()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        # Initialize loaders
        self.pdf_loader = PDFLoader()
        self.docx_loader = DocxLoader()
        self.txt_loader = TxtLoader()
        self.web_loader = WebLoader()

    def process_file(self, file_path: str) -> List[Document]:
        """Process a file based on its extension."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == ".pdf":
            text = self.pdf_loader.load(str(file_path))
        elif extension in [".docx", ".doc"]:
            text = self.docx_loader.load(str(file_path))
        elif extension in [".txt"]:
            text = self.txt_loader.load(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {extension}")
        
        # Create metadata
        metadata = {
            "source": str(file_path),
            "file_type": extension,
            "file_name": file_path.name,
            "document_id": str(uuid.uuid4())
        }
        
        # Create a document and split it
        doc = Document(page_content=text, metadata=metadata)
        return self.split_document(doc)
    
    def process_url(self, url: str) -> List[Document]:
        """Process a web URL."""
        try:
            text = self.web_loader.load(url)
            
            # Create metadata
            metadata = {
                "source": url,
                "file_type": "web",
                "document_id": str(uuid.uuid4())
            }
            
            # Create a document and split it
            doc = Document(page_content=text, metadata=metadata)
            return self.split_document(doc)
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            raise
    
    def split_document(self, document: Document) -> List[Document]:
        """Split a document into chunks."""
        return self.text_splitter.split_documents([document])
    
    def process_documents(self, file_paths: List[str], urls: Optional[List[str]] = None) -> List[Document]:
        """Process multiple documents and URLs."""
        documents = []
        
        # Process files
        for file_path in file_paths:
            try:
                docs = self.process_file(file_path)
                documents.extend(docs)
                logger.info(f"Processed file: {file_path}, generated {len(docs)} chunks")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
        
        # Process URLs
        if urls:
            for url in urls:
                try:
                    docs = self.process_url(url)
                    documents.extend(docs)
                    logger.info(f"Processed URL: {url}, generated {len(docs)} chunks")
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {str(e)}")
        
        return documents

# import os
# from typing import List, Dict, Any, Optional
# from pathlib import Path
# import uuid
# import logging

# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document

# from .loaders import PDFLoader, DocxLoader, WebLoader, TxtLoader
# from ..config import CHUNK_SIZE, CHUNK_OVERLAP

# logger = logging.getLogger(__name__)

# class DocumentProcessor:
#     """Main document processing class that handles different document types."""
    
#     def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             length_function=len,
#         )
        
#         # Initialize loaders
#         self.pdf_loader = PDFLoader().load()
#         self.docx_loader = DocxLoader().load()
#         self.web_loader = WebLoader().load()
#         self.TxtLoader = TxtLoader().load()
        
#     def process_file(self, file_path: str) -> List[Document]:
#         """Process a file based on its extension."""
#         file_path = Path(file_path)
        
#         if not file_path.exists():
#             raise FileNotFoundError(f"File not found: {file_path}")
        
#         extension = file_path.suffix.lower()
        
#         if extension == '.pdf':
#             text = self.pdf_loader.load(str(file_path))
#         elif extension in ['.docx', '.doc']:
#             text = self.docx_loader.load(str(file_path))
#         else:
#             raise ValueError(f"Unsupported file type: {extension}")
        
#         # Create metadata
#         metadata = {
#             "source": str(file_path),
#             "file_type": extension,
#             "file_name": file_path.name,
#             "document_id": str(uuid.uuid4())
#         }
        
#         # Create a document and split it
#         doc = Document(page_content=text, metadata=metadata)
#         return self.split_document(doc)
    
#     def process_url(self, url: str) -> List[Document]:
#         """Process a web URL."""
#         try:
#             text = self.web_loader.load(url)
            
#             # Create metadata
#             metadata = {
#                 "source": url,
#                 "file_type": "web",
#                 "document_id": str(uuid.uuid4())
#             }
            
#             # Create a document and split it
#             doc = Document(page_content=text, metadata=metadata)
#             return self.split_document(doc)
            
#         except Exception as e:
#             logger.error(f"Error processing URL {url}: {str(e)}")
#             raise
    
#     def split_document(self, document: Document) -> List[Document]:
#         """Split a document into chunks."""
#         return self.text_splitter.split_documents([document])
    
#     def process_documents(self, file_paths: List[str], urls: Optional[List[str]] = None) -> List[Document]:
#         """Process multiple documents and URLs."""
#         documents = []
        
#         # Process files
#         for file_path in file_paths:
#             try:
#                 docs = self.process_file(file_path)
#                 documents.extend(docs)
#                 logger.info(f"Processed file: {file_path}, generated {len(docs)} chunks")
#             except Exception as e:
#                 logger.error(f"Error processing file {file_path}: {str(e)}")
        
#         # Process URLs
#         if urls:
#             for url in urls:
#                 try:
#                     docs = self.process_url(url)
#                     documents.extend(docs)
#                     logger.info(f"Processed URL: {url}, generated {len(docs)} chunks")
#                 except Exception as e:
#                     logger.error(f"Error processing URL {url}: {str(e)}")
        
#         return documents