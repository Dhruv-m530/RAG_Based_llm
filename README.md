# RAG System with LangChain and Ollama

A Python-based Retrieval-Augmented Generation (RAG) system using LangChain that processes PDFs, DOCX files, and article links to provide responses based on extracted content. This system is configured to use Ollama for local LLM inference.

## Features

- Document processing for PDFs, DOCX files, and web articles
- Vector storage using FAISS or ChromaDB
- Integration with Ollama for local LLM inference
- SentenceTransformers for embeddings (with optional Ollama embeddings)
- FastAPI backend for querying the system
- React frontend for easy interaction
- Docker support for containerization and deployment

## Project Structure

```
.
├── data/                  # Data storage
│   ├── documents/         # Uploaded documents
│   └── vectordb/          # Vector database storage
├── src/                   # Source code
│   ├── api/               # FastAPI application
│   ├── document_processor/ # Document processing modules
│   ├── embeddings/        # Embedding models
│   ├── llm/               # LLM integration
│   ├── rag/               # RAG chain implementation
│   ├── vectorstore/       # Vector store implementations
│   ├── config.py          # Configuration
│   └── main.py            # Application entry point
├── .env                   # Environment variables
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- Docker (optional)
- Ollama installed and running locally

### Local Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd rag-system
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

5. Edit the `.env` file to configure your settings.

6. Install and run Ollama:

```bash
# Follow instructions at https://ollama.ai/download
# Then pull the model you want to use
ollama pull mistral
```

### Running with Docker

1. Build and start the Docker container:

```bash
docker-compose up -d
```

2. The API will be available at `http://localhost:8000`.

## Usage

### API Endpoints

- `POST /query`: Query the RAG system with a question
- `POST /upload`: Upload and process documents (PDF, DOCX)
- `POST /process-urls`: Process web URLs

### Example Queries

#### Query the RAG system

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

#### Upload documents

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "files=@/path/to/document.pdf" \
  -F "files=@/path/to/another.docx"
```

#### Process URLs

```bash
curl -X POST "http://localhost:8000/process-urls" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/article", "https://example.com/another-article"]}'
```

## Configuration

The system can be configured through environment variables in the `.env` file:

- `LLM_MODE`: "local" or "api"
- `LOCAL_MODEL_NAME`: Name of the Ollama model to use (e.g., "mistral")
- `USE_OLLAMA`: Set to "true" to use Ollama for LLM inference
- `EMBEDDING_MODE`: "local" or "api"
- `LOCAL_EMBEDDING_MODEL`: Name of the local embedding model
- `VECTOR_DB_PATH`: Path to store vector database
- `HOST`: Host to bind the server to
- `PORT`: Port to bind the server to

## Using Different Ollama Models

To use a different Ollama model:

1. Pull the model using Ollama CLI:

```bash
ollama pull llama3
```

2. Update the `LOCAL_MODEL_NAME` in your `.env` file:

```
LOCAL_MODEL_NAME=llama3
```

## License

[MIT License](LICENSE)# RAG_Based_llm
