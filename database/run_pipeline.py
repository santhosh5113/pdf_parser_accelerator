# database/run_pipeline.py

import sys
import subprocess
import os
import glob
import json
import argparse
import time
from typing import List, Dict, Any
from config.vector_store_config import (
    VECTOR_STORE_CONFIG,
    CHROMA_CONFIG,
    QDRANT_CONFIG,
    WEAVIATE_CONFIG,
    MILVUS_CONFIG,
    FAISS_CONFIG,
    PINECONE_CONFIG
)
from .text_chunker import process_pdf_json, chunk_text, extract_text_from_json
from .vector_store_factory import VectorStoreFactory
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...")
    subprocess.run(["pip", "install", "PyMuPDF"])
    import fitz

# Map of vector store names to their configurations
VECTOR_STORE_CONFIGS = {
    "chroma": CHROMA_CONFIG,
    "qdrant": QDRANT_CONFIG,
    "weaviate": WEAVIATE_CONFIG,
    "milvus": MILVUS_CONFIG,
    "faiss": FAISS_CONFIG,
    "pinecone": PINECONE_CONFIG
}

def get_vector_store_config(store_type: str) -> Dict[str, Any]:
    """Get configuration for specified vector store type."""
    if store_type not in VECTOR_STORE_CONFIGS:
        available_stores = ", ".join(VECTOR_STORE_CONFIGS.keys())
        raise ValueError(f"Unsupported vector store type: {store_type}. Available types: {available_stores}")
    return VECTOR_STORE_CONFIGS[store_type]

def run_parser(env_name, script, input_pdf, output_json):
    subprocess.run([
        "conda", "run", "-n", env_name, "python",
        f"parsers/{script}", input_pdf, output_json
    ])

def analyze_pdf(pdf_path: str) -> str:
    """Analyze PDF and determine its category."""
    try:
        doc = fitz.open(pdf_path)
        
        # Check first page
        page = doc[0]
        
        # Get text
        text = page.get_text()
        
        # Get images
        images = page.get_images()
        
        # Check for tables (simplified check)
        has_tables = False
        try:
            tables = page.find_tables()
            has_tables = tables is not None and tables.tables
        except:
            pass
        
        doc.close()
        
        # Decision logic
        if not text.strip():  # No text found
            return "scanned_pdf"
        elif has_tables:
            return "native_table"
        else:
            return "native_text"
            
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return "unknown"

def store_pdf_chunks(json_path: str, source_id: str, vector_store_type: str) -> bool:
    """Store PDF chunks in vector database.
    
    Args:
        json_path: Path to JSON file containing extracted text
        source_id: Source identifier for the file
        vector_store_type: Type of vector store to use
        
    Returns:
        bool: True if storage was successful
    """
    try:
        config = get_vector_store_config(vector_store_type)
        return process_pdf_json(json_path, source_id, config)
    except Exception as e:
        print(f"Error storing chunks: {e}")
        return False

def manage_docker_services(vector_store: str, action: str = "start") -> bool:
    """Start or stop Docker services for the specified vector store.
    
    Args:
        vector_store: Name of the vector store
        action: Either "start" or "stop"
        
    Returns:
        bool: True if successful
    """
    docker_dirs = {
        "milvus": "docker/milvus",
        "qdrant": "docker/qdrant",
        "weaviate": "docker/weaviate"
    }
    
    if vector_store not in docker_dirs:
        return True  # No Docker services needed
        
    try:
        docker_dir = docker_dirs[vector_store]
        if not os.path.exists(docker_dir):
            print(f"❌ Docker configuration not found for {vector_store}")
            return False
            
        # Change to Docker directory
        cwd = os.getcwd()
        os.chdir(docker_dir)
        
        if action == "start":
            # Stop and remove existing containers first
            print(f"🧹 Cleaning up existing {vector_store} services...")
            subprocess.run(["docker-compose", "down", "-v"], check=False)
            
            # Start services
            print(f"🐳 Starting {vector_store} services...")
            subprocess.run(["docker-compose", "up", "-d", "--force-recreate", "--remove-orphans"], check=True)
            
            # Wait for services to be ready
            time.sleep(15)  # Increased wait time for services to initialize
            
        elif action == "stop":
            print(f"🐳 Stopping {vector_store} services...")
            subprocess.run(["docker-compose", "down", "-v"], check=True)
            
        # Return to original directory
        os.chdir(cwd)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error managing Docker services: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error managing Docker services: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="PDF Processing Pipeline")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_json", help="Path for output JSON file")
    parser.add_argument(
        "--vector-store", 
        choices=list(VECTOR_STORE_CONFIGS.keys()),
        default="milvus",
        help="Vector store backend to use"
    )
    args = parser.parse_args()

    # Start required Docker services
    if not manage_docker_services(args.vector_store, "start"):
        print("❌ Failed to start required services")
        return

    try:
        category = analyze_pdf(args.input_pdf)
        print(f"📊 Detected category: {category}")

        # Route to appropriate parser
        if category == "scanned_pdf":
            run_parser("llama_parse_env", "llama_parser.py", args.input_pdf, args.output_json)
        elif category == "native_table":
            run_parser("docling_env", "docling_parser.py", args.input_pdf, args.output_json)
        elif category == "native_text":
            run_parser("pdfminer_env", "pdfminer_parser.py", args.input_pdf, args.output_json)
        else:
            print("❌ Unable to determine suitable parser for this PDF.")
            return

        # Store output in vector DB
        success = store_pdf_chunks(args.output_json, os.path.basename(args.input_pdf), args.vector_store)
        if success:
            print(f"✅ Successfully stored in {args.vector_store} vector database")
        else:
            print(f"❌ Failed to store in {args.vector_store} vector database")

    finally:
        # Stop Docker services
        manage_docker_services(args.vector_store, "stop")

if __name__ == "__main__":
    main()
 