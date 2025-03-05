import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(DATA_DIR / "vectordb"))

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)
Path(VECTOR_DB_PATH).mkdir(exist_ok=True, parents=True)

# LLM settings
LLM_MODE = os.getenv("LLM_MODE", "local")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "mistral")
API_MODEL_NAME = os.getenv("API_MODEL_NAME", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

# Embedding settings
EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "local")
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
API_EMBEDDING_MODEL = os.getenv("API_EMBEDDING_MODEL", "")

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval settings
TOP_K_RETRIEVAL = 5