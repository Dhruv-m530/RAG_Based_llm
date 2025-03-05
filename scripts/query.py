#!/usr/bin/env python
"""
Script to query the RAG system from the command line.
"""
import argparse
import logging
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.rag import RAGChain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Query the RAG system")
    
    # Add arguments
    parser.add_argument(
        "question",
        help="Question to ask the RAG system"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    args = parse_args()
    
    try:
        # Create RAG chain
        rag_chain = RAGChain()
        
        # Query the system
        result = rag_chain.query(args.question)
        
        # Print the answer
        print("\n" + "="*80)
        print("ANSWER:")
        print("="*80)
        print(result["answer"])
        print("\n" + "="*80)
        
        # Print the sources
        print("SOURCES:")
        print("="*80)
        for i, source in enumerate(result["sources"], 1):
            print(f"Source {i}:")
            print(f"  Content: {source['content']}")
            print(f"  Metadata: {source['metadata']}")
            print()
        
    except Exception as e:
        logger.error(f"Error querying RAG system: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()