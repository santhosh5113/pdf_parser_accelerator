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
from .vector_store_factory import VectorStoreFactory
# Do NOT import analyzer.analyze_pdf or text_chunker at the top level

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
    parser.add_argument("--vector-store", choices=list(VECTOR_STORE_CONFIGS.keys()), default="milvus")
    parser.add_argument("--store-only", action="store_true", help="Only run the storage step (for internal use)")
    args = parser.parse_args()

    env_map = {
        "milvus": "milvus_env",
        "chroma": "chroma_env",
        "weaviate": "weaviate_env",
        "qdrant": "qdrant_env",
        "faiss": "faiss_env"
    }
    current_env = os.environ.get("CONDA_DEFAULT_ENV")
    required_env = env_map.get(args.vector_store, None)
    print("[DEBUG] Current CONDA_DEFAULT_ENV:", current_env)
    print("[DEBUG] sys.executable:", sys.executable)
    print("[DEBUG] Selected vector store:", args.vector_store)
    print("[DEBUG] Required environment for this vector store:", required_env)
    if required_env:
        if current_env == required_env:
            print(f"[DEBUG] ✅ Correct environment '{required_env}' is already activated.")
        else:
            print(f"[DEBUG] ❌ Current environment ('{current_env}') does not match required ('{required_env}'). Will attempt to switch.")
    else:
        print("[DEBUG] No specific environment required for this vector store.")

    if args.store_only:
        # Only do storage (in the vector DB environment)
        from .text_chunker import process_pdf_json
        config = get_vector_store_config(args.vector_store)
        success = process_pdf_json(args.output_json, os.path.basename(args.input_pdf), config)
        if success:
            print(f"✅ Successfully stored in {args.vector_store} vector database")
        else:
            print(f"❌ Failed to store in {args.vector_store} vector database")
        return

    # PHASE 1: Analysis and parsing (in pipeline_env)
    from analyzer.analyze_pdf import analyze_pdf
    category = analyze_pdf(args.input_pdf)
    print(f"📊 Detected category: {category}")

    # Route to appropriate parser (still in pipeline_env)
    if category == "scanned_pdf":
        run_parser("llama_parse_env", "llama_parser.py", args.input_pdf, args.output_json)
    elif category == "native_table":
        run_parser("docling_env", "docling_parser.py", args.input_pdf, args.output_json)
    elif category == "native_text":
        run_parser("pdfminer_env", "pdfminer_parser.py", args.input_pdf, args.output_json)
    else:
        print("❌ Unable to determine suitable parser for this PDF.")
        return

    # PHASE 2: Switch to vector DB environment for storage
    if args.vector_store in env_map and current_env != env_map[args.vector_store]:
        print(f"🔄 Switching to {env_map[args.vector_store]} for {args.vector_store} backend...")
        cmd = [
            "conda", "run", "-n", env_map[args.vector_store], "python", "-m", "database.run_pipeline",
            args.input_pdf,
            args.output_json,
            "--vector-store", args.vector_store,
            "--store-only"
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(cmd, env=env)
        return

    # If already in the correct environment, run storage step directly
    from .text_chunker import process_pdf_json
    config = get_vector_store_config(args.vector_store)
    success = process_pdf_json(args.output_json, os.path.basename(args.input_pdf), config)
    if success:
        print(f"✅ Successfully stored in {args.vector_store} vector database")
    else:
        print(f"❌ Failed to store in {args.vector_store} vector database")

if __name__ == "__main__":
    main()
 