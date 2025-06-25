"""Configuration for vector store settings."""

from typing import Dict, Any

# Common configuration
COMMON_CONFIG = {
    "collection_name": "pdf_chunks",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
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
    "location": "http://localhost:6333",
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


# Chunk configuration
CHUNK_CONFIG = {
    "max_tokens": 512,  # Maximum tokens per chunk
    "overlap": 50  # Number of overlapping tokens between chunks
}

# Pinecone configuration
PINECONE_CONFIG: Dict[str, Any] = {
    **COMMON_CONFIG,
    "type": "pinecone",
    "api_key": "<YOUR_PINECONE_API_KEY>",
    "environment": "<YOUR_PINECONE_ENVIRONMENT>",
    "index_name": "pdf_chunks"
}

# Active configuration (uncomment one of these lines to switch between backends)
# VECTOR_STORE_CONFIG = CHROMA_CONFIG  # Use ChromaDB backend
# VECTOR_STORE_CONFIG = QDRANT_CONFIG  # Use Qdrant backend
# VECTOR_STORE_CONFIG = WEAVIATE_CONFIG  # Use Weaviate backend
# VECTOR_STORE_CONFIG = MILVUS_CONFIG  # Use Milvus backend 
VECTOR_STORE_CONFIG = PINECONE_CONFIG  # Use Pinecone backend