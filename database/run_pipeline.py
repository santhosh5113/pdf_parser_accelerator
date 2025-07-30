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
    FAISS_CONFIG
)
from .vector_store_factory import VectorStoreFactory
# Do NOT import analyzer.analyze_pdf or text_chunker at the top level

# --- PDF to image conversion helper ---
def pdf_to_images(pdf_path: str, output_dir: str) -> List[str]:
    """Convert a PDF to images (one per page) and return list of image paths."""
    from pdf2image import convert_from_path
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_dir, f"page_{i+1}.png")
        img.save(img_path, "PNG")
        image_paths.append(img_path)
    return image_paths

# Map of vector store names to their configurations
VECTOR_STORE_CONFIGS = {
    "chroma": CHROMA_CONFIG,
    "qdrant": QDRANT_CONFIG,
    "weaviate": WEAVIATE_CONFIG,
    "milvus": MILVUS_CONFIG,
    "faiss": FAISS_CONFIG
}

def get_vector_store_config(store_type: str) -> Dict[str, Any]:
    """Get configuration for specified vector store type."""
    if store_type not in VECTOR_STORE_CONFIGS:
        available_stores = ", ".join(VECTOR_STORE_CONFIGS.keys())
        raise ValueError(f"Unsupported vector store type: {store_type}. Available types: {available_stores}")
    return VECTOR_STORE_CONFIGS[store_type]

def run_parser(env_name, script, input_pdf, output_json, extra_args=None):
    cmd = [
        "conda", "run", "-n", env_name, "python",
        f"parsers/{script}", input_pdf, output_json
    ]
    if extra_args:
        cmd.extend(extra_args)
    
    # Capture output to prevent duplicate printing
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print stdout if there's output
    if result.stdout:
        print(result.stdout, end='')
    
    # Print stderr if there are errors
    if result.stderr:
        print(result.stderr, end='')
    
    # Check return code
    if result.returncode != 0:
        print(f"❌ Parser {script} failed with return code {result.returncode}")
        return False
    
    return True

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
            subprocess.run(["docker-compose", "down", "-v"], check=False, capture_output=True)
            
            # Start services
            print(f"🐳 Starting {vector_store} services...")
            subprocess.run(["docker-compose", "up", "-d", "--force-recreate", "--remove-orphans"], check=True, capture_output=True)
            
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
    # ===== QUICK SWITCHING: Change default analyzer here =====
    # Uncomment the analyzer you want to use as default:
    DEFAULT_ANALYZER = "openai_vlm"  # OpenAI VLM (requires API key)
    #DEFAULT_ANALYZER = "ollama"     # Ollama (local, no API key needed)
    # DEFAULT_ANALYZER = "clip"       # CLIP (local, no API key needed)
    
    parser = argparse.ArgumentParser(description="PDF Processing Pipeline")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_json", help="Path for output JSON file")
    parser.add_argument("--vector-store", choices=list(VECTOR_STORE_CONFIGS.keys()), default="milvus")
    parser.add_argument("--store-only", action="store_true", help="Only run the storage step (for internal use)")

    parser.add_argument("--analyzer", choices=["ollama", "clip", "openai_vlm"], default=DEFAULT_ANALYZER, help="PDF analyzer to use")
    parser.add_argument("--openai-model", type=str, default="gpt-4o", help="OpenAI model for VLM analysis")
    

    args = parser.parse_args()

    # Handle store-only mode FIRST
    if args.store_only:
        from .text_chunker import process_pdf_json
        config = get_vector_store_config(args.vector_store)
        success = process_pdf_json(args.output_json, os.path.basename(args.input_pdf), config)
        if success:
            print(f"✅ Successfully stored in {args.vector_store} vector database")
        else:
            print(f"❌ Failed to store in {args.vector_store} vector database")
        return  # Exit immediately after storage

    env_map = {
        "milvus": "milvus_env",
        "chroma": "chroma_env",
        "weaviate": "weaviate_env",
        "qdrant": "qdrant_env",
        "faiss": "faiss_env"
    }
    current_env = os.environ.get("CONDA_DEFAULT_ENV")
    required_env = env_map.get(args.vector_store, None)

    # PHASE 1: Analysis and parsing (in pipeline_env)
    
    # ===== OPENAI VLM ANALYZER =====
    if args.analyzer == "openai_vlm":
        from analyzer.analyze_pdf4 import classify_pdf_with_openai_vlm
        results = classify_pdf_with_openai_vlm(args.input_pdf, model=args.openai_model, save_results=False)
        if "error" not in results:
            category = results["overall_classification"]
            print(f"📊 Detected category (OpenAI VLM): {category}")
        else:
            print(f"❌ OpenAI VLM analysis failed: {results['error']}")
            return
    
    # ===== OLLAMA ANALYZER =====
    elif args.analyzer == "ollama":
        from analyzer.analyze_pdf2 import analyze_pdf_with_ollama as analyze_pdf
        category = analyze_pdf(args.input_pdf)
        print(f"📊 Detected category (Ollama): {category}")
    
    # ===== CLIP ANALYZER =====
    elif args.analyzer == "clip":
        from analyzer.analyze_pdf3 import classify_pdf_pages
        # Note: CLIP returns per-page results, need to aggregate
        results = classify_pdf_pages(args.input_pdf, device="cpu")
        if results:
            # Aggregate page results to get overall category
            from collections import Counter
            classifications = [r["prediction"] for r in results]
            category_counts = Counter(classifications)
            category = category_counts.most_common(1)[0][0]
            print(f"📊 Detected category (CLIP): {category}")
        else:
            print("❌ CLIP analysis failed")
            return

    # Route to appropriate parser (still in pipeline_env)
    category = category.replace(" ", "_").lower()
    parser_success = False
    
    if category == "native_text":
        parser_success = run_parser("mupdf_env", "mupdf_parser.py", args.input_pdf, args.output_json)
    elif category == "native_table":
        parser_success = run_parser("docling_env", "docling_parser.py", args.input_pdf, args.output_json)
    elif category == "native_math_heavy":
        parser_success = run_parser("landingai_env", "landingai_parser.py", args.input_pdf, args.output_json)
    elif category == "scanned_math_heavy":
        parser_success = run_parser("landingai_env", "landingai_parser.py", args.input_pdf, args.output_json)
    elif category == "scanned_text":
        parser_success = run_parser("llama_parse_env", "llama_parser.py", args.input_pdf, args.output_json)
    elif category == "scanned_table":
        parser_success = run_parser("llama_parse_env", "llama_parser.py", args.input_pdf, args.output_json)
    else:
        print(f"❌ Unable to determine suitable parser for category: '{category}'")
        print(f"   Available categories: native_text, native_table, native_math_heavy, scanned_math_heavy, scanned_text, scanned_table")
        return
    
    if not parser_success:
        print(f"❌ Parser failed for category: {category}")
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
        
        # Capture output to prevent duplicate printing
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        # Print stdout if there's output
        if result.stdout:
            print(result.stdout, end='')
        
        # Print stderr if there are errors
        if result.stderr:
            print(result.stderr, end='')
        
        # Check return code
        if result.returncode != 0:
            print(f"❌ Storage step failed with return code {result.returncode}")
        
        return  # Ensure parent process exits after switching environments

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
 