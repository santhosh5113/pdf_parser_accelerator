"""Configuration settings for the PDF parser."""

import os

# Vector store settings
VECTOR_STORE_CONFIG = {
    "type": os.getenv("VECTOR_STORE_TYPE", "faiss"),
    "collection_name": "pdf_chunks",
    "embedding_model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"),
    "index_path": os.getenv("FAISS_INDEX_PATH", "./faiss_index")
}

# PDF processing settings
PDF_PROCESSING_CONFIG = {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "min_chunk_size": 100
}

# File storage settings
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "./processed")

# API settings
API_CONFIG = {
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_extensions": [".pdf"],
    "max_results": 5
}

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_CONFIG["index_path"], exist_ok=True) 