import logging
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    PDFPlumberLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
    TextLoader,
)


logger = logging.getLogger(__name__)

class PDFLoader:
    """Loader for PDF documents using LangChain with PyMuPDF and pdfplumber fallback."""
    
    def load(self, file_path: str) -> str:
        """Extract text from a PDF file using LangChain loaders."""
        try:
            return self._load_with_pymupdf(file_path)
        except Exception as e:
            logger.warning(f"PyMuPDF failed, falling back to pdfplumber: {str(e)}")
            try:
                return self._load_with_pdfplumber(file_path)
            except Exception as e:
                logger.error(f"Failed to extract text from PDF {file_path}: {str(e)}")
                raise
    
    def _load_with_pymupdf(self, file_path: str) -> str:
        """Extract text using LangChain's PyMuPDFLoader."""
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        return "\n".join(doc.page_content for doc in documents)

    def _load_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using LangChain's PDFPlumberLoader."""
        loader = PDFPlumberLoader(file_path)
        documents = loader.load()
        return "\n".join(doc.page_content for doc in documents)


class DocxLoader:
    """Loader for DOCX documents using LangChain."""
    
    def load(self, file_path: str) -> str:
        """Extract text from a DOCX file using LangChain's UnstructuredWordDocumentLoader."""
        try:
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
            return "\n".join(doc.page_content for doc in documents)
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX {file_path}: {str(e)}")
            raise


class TxtLoader:
    """Loader for TXT files using LangChain."""
    
    def load(self, file_path: str) -> str:
        """Extract text from a TXT file using LangChain's TextLoader."""
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            return "\n".join(doc.page_content for doc in documents)
        except Exception as e:
            logger.error(f"Failed to extract text from TXT {file_path}: {str(e)}")
            raise


class WebLoader:
    """Loader for web content using LangChain's NewspaperLoader with fallback to WebBaseLoader."""
    
    def load(self, url: str) -> str:
        """Extract text from a web URL using LangChain."""
        try:
            return self._load_with_newspaper(url)
        except Exception as e:
            logger.warning(f"Newspaper3k failed, falling back to WebBaseLoader: {str(e)}")
            try:
                return self._load_with_webbaseloader(url)
            except Exception as e:
                logger.error(f"Failed to extract text from URL {url}: {str(e)}")
                raise
    
    def _load_with_newspaper(self, url: str) -> str:
        """Extract text using LangChain's NewspaperLoader."""
        loader = NewspaperLoader(url)
        documents = loader.load()
        return "\n".join(doc.page_content for doc in documents)

    def _load_with_webbaseloader(self, url: str) -> str:
        """Extract text using LangChain's WebBaseLoader."""
        loader = WebBaseLoader(url)
        documents = loader.load()
        return "\n".join(doc.page_content for doc in documents)

# import logging
# from typing import Optional

# # PDF processing
# import fitz  # PyMuPDF
# import pdfplumber

# # DOCX processing
# import docx

# # Web processing
# import requests
# from bs4 import BeautifulSoup
# from newspaper import Article
# import time

# logger = logging.getLogger(__name__)

# class PDFLoader:
#     """Loader for PDF documents using PyMuPDF with fallback to pdfplumber."""
    
#     def load(self, file_path: str) -> str:
#         """Extract text from a PDF file."""
#         try:
#             # Try PyMuPDF first (faster)
#             return self._load_with_pymupdf(file_path)
#         except Exception as e:
#             logger.warning(f"PyMuPDF failed, falling back to pdfplumber: {str(e)}")
#             try:
#                 # Fallback to pdfplumber
#                 return self._load_with_pdfplumber(file_path)
#             except Exception as e:
#                 logger.error(f"Failed to extract text from PDF {file_path}: {str(e)}")
#                 raise
    
#     def _load_with_pymupdf(self, file_path: str) -> str:
#         """Extract text using PyMuPDF."""
#         text = ""
#         with fitz.open(file_path) as doc:
#             for page in doc:
#                 text += page.get_text()
#         return text
    
#     def _load_with_pdfplumber(self, file_path: str) -> str:
#         """Extract text using pdfplumber."""
#         text = ""
#         with pdfplumber.open(file_path) as pdf:
#             for page in pdf.pages:
#                 text += page.extract_text() or ""
#         return text


# class DocxLoader:
#     """Loader for DOCX documents."""
    
#     def load(self, file_path: str) -> str:
#         """Extract text from a DOCX file."""
#         try:
#             doc = docx.Document(file_path)
#             return "\n".join([paragraph.text for paragraph in doc.paragraphs])
#         except Exception as e:
#             logger.error(f"Failed to extract text from DOCX {file_path}: {str(e)}")
#             raise


# class WebLoader:
#     """Loader for web content using Newspaper3k with fallback to BeautifulSoup."""
    
#     def load(self, url: str) -> str:
#         """Extract text from a web URL."""
#         try:
#             # Try Newspaper3k first (better content extraction)
#             return self._load_with_newspaper(url)
#         except Exception as e:
#             logger.warning(f"Newspaper3k failed, falling back to BeautifulSoup: {str(e)}")
#             try:
#                 # Fallback to BeautifulSoup
#                 return self._load_with_beautifulsoup(url)
#             except Exception as e:
#                 logger.error(f"Failed to extract text from URL {url}: {str(e)}")
#                 raise
    
#     def _load_with_newspaper(self, url: str) -> str:
#         """Extract text using Newspaper3k."""
#         article = Article(url)
#         article.download()
#         # Add a small delay to ensure download completes
#         time.sleep(1)
#         article.parse()
        
#         # Combine title, text and any other useful content
#         content = []
#         if article.title:
#             content.append(f"Title: {article.title}")
#         if article.text:
#             content.append(article.text)
        
#         return "\n\n".join(content)
    
#     def _load_with_beautifulsoup(self, url: str) -> str:
#         """Extract text using BeautifulSoup."""
#         response = requests.get(url, headers={
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         })
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, "html.parser")
        
#         # Remove script and style elements
#         for script in soup(["script", "style"]):
#             script.extract()
        
#         # Get text
#         text = soup.get_text(separator="\n")
        
#         # Break into lines and remove leading and trailing space
#         lines = (line.strip() for line in text.splitlines())
#         # Break multi-headlines into a line each
#         chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#         # Remove blank lines
#         text = "\n".join(chunk for chunk in chunks if chunk)
        
#         return text