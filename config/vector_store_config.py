"""Configuration for vector store settings."""

from typing import Dict, Any
import os

# Common configuration
COMMON_CONFIG = {
    "collection_name": "pdf_chunks",
    "embedding_model": "BAAI/bge-base-en-v1.5"
}

# ChromaDB configuration
CHROMA_CONFIG: Dict[str, Any] = {
    **COMMON_CONFIG,
    "type": "chroma",
    "db_path": "./chroma_db"
}

# Qdrant configuration
QDRANT_CONFIG: Dict[str, Any] = {
    **COMMON_CONFIG,
    "type": "qdrant",
    "location": "https://a2cb6e04-027f-467e-8b2b-d072eb273104.us-west-1-0.aws.cloud.qdrant.io",  # Qdrant Cloud URL
    "api_key": os.getenv("QDRANT_API_KEY"),
    "use_sparse": True  # Enable hybrid search
}

# Weaviate configuration
WEAVIATE_CONFIG: Dict[str, Any] = {
    **COMMON_CONFIG,
    "type": "weaviate",
    "host": "localhost",  # Default Weaviate server host
    "port": 8080,          # Default Weaviate server port
    "secure": False        # Use HTTP by default
}

# Milvus configuration
MILVUS_CONFIG: Dict[str, Any] = {
    **COMMON_CONFIG,
    "type": "milvus",
    "host": "localhost",  # Default Milvus server host
    "port": 19530  # Default Milvus server port
}

# FAISS configuration
FAISS_CONFIG: Dict[str, Any] = {
    **COMMON_CONFIG,
    "type": "faiss",
    "index_path": "./faiss_index",  # Path to store FAISS index
    "dimension": 384  # Dimension of embeddings from MiniLM-L6-v2
}


# Chunk configuration (character-based)
CHUNK_CONFIG = {
    "max_tokens": 1000,  # Maximum characters per chunk
    "overlap": 200,      # Number of overlapping characters between chunks
    "min_tokens": 100    # Minimum characters per chunk
}



# Active configuration (uncomment one of these lines to switch between backends)
VECTOR_STORE_CONFIG = CHROMA_CONFIG  # Use ChromaDB backend
# VECTOR_STORE_CONFIG = QDRANT_CONFIG  # Use Qdrant backend
# VECTOR_STORE_CONFIG = WEAVIATE_CONFIG  # Use Weaviate backend
# VECTOR_STORE_CONFIG = MILVUS_CONFIG  # Use Milvus backend 