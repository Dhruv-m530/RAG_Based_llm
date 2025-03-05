#!/usr/bin/env python
"""
Script to ingest documents into the RAG system.
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List

# Add the parent directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.document_processor import DocumentProcessor
from src.rag import RAGChain
from src.config import DOCUMENTS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG system")
    
    # Add arguments
    parser.add_argument(
        "--files", "-f",
        nargs="+",
        help="Paths to files to ingest"
    )
    
    parser.add_argument(
        "--urls", "-u",
        nargs="+",
        help="URLs to ingest"
    )
    
    parser.add_argument(
        "--directory", "-d",
        help="Directory containing files to ingest"
    )
    
    return parser.parse_args()

def get_files_from_directory(directory: str) -> List[str]:
    """Get all PDF and DOCX files from a directory."""
    directory_path = Path(directory)
    if not directory_path.exists() or not directory_path.is_dir():
        raise ValueError(f"Directory not found: {directory}")
    
    files = []
    for ext in [".pdf", ".docx", ".doc"]:
        files.extend([str(f) for f in directory_path.glob(f"**/*{ext}")])
    
    return files

def main():
    """Main entry point for the script."""
    args = parse_args()
    
    # Check if at least one source is provided
    if not args.files and not args.urls and not args.directory:
        logger.error("No files or URLs provided. Use --files, --urls, or --directory")
        sys.exit(1)
    
    # Get files from directory if provided
    files = []
    if args.directory:
        try:
            files = get_files_from_directory(args.directory)
            logger.info(f"Found {len(files)} files in directory {args.directory}")
        except Exception as e:
            logger.error(f"Error getting files from directory: {str(e)}")
            sys.exit(1)
    
    # Add individual files if provided
    if args.files:
        files.extend(args.files)
    
    # Get URLs if provided
    urls = args.urls or []
    
    # Check if we have any sources
    if not files and not urls:
        logger.error("No valid files or URLs found")
        sys.exit(1)
    
    logger.info(f"Ingesting {len(files)} files and {len(urls)} URLs")
    
    try:
        # Create processor and RAG chain
        document_processor = DocumentProcessor()
        rag_chain = RAGChain()
        
        # Process documents
        documents = document_processor.process_documents(files, urls)
        logger.info(f"Processed {len(documents)} document chunks")
        
        # Add to vector store
        rag_chain.add_documents(documents)
        logger.info("Documents added to vector store successfully")
        
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()