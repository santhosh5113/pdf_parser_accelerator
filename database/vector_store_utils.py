"""Utility functions for managing vector store data."""

import json
from typing import Dict, Any, List
from config.vector_store_config import VECTOR_STORE_CONFIG
from .vector_store_factory import VectorStoreFactory

def list_all_chunks(config: Dict[str, Any] = VECTOR_STORE_CONFIG):
    """List all chunks stored in the vector store.
    
    Args:
        config: Vector store configuration (defaults to active config)
    """
    # Create vector store instance
    vector_store = VectorStoreFactory.create(**config)
    
    # Get all chunks
    chunks = vector_store.get_all_chunks()
    
    print(f"🧠 Found {len(chunks)} chunks in {config['type']} vector store.\n")
    
    for chunk in chunks:
        print(f"🔹 ID: {chunk['id']}")
        print(f"📄 Document: {chunk['text']}")
        print(f"📝 Metadata: {chunk['metadata']}")
        print("-" * 50)
    
    return chunks

def export_chunks(output_path: str = "exported_chunks.json", 
                 config: Dict[str, Any] = VECTOR_STORE_CONFIG):
    """Export all chunks to a JSON file.
    
    Args:
        output_path: Path to save the exported JSON file
        config: Vector store configuration (defaults to active config)
    """
    # Get all chunks
    chunks = list_all_chunks(config)
    
    # Format for export
    exported = []
    for chunk in chunks:
        exported.append({
            "id": chunk["id"],
            "content": chunk["text"],
            "source": chunk["metadata"].get("source", "unknown"),
            "metadata": chunk["metadata"]
        })
    
    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(exported, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(exported)} chunks to '{output_path}'")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector store utility functions")
    parser.add_argument("action", choices=["list", "export"], 
                       help="Action to perform (list or export chunks)")
    parser.add_argument("--output", "-o", default="exported_chunks.json",
                       help="Output file path for export action")
    args = parser.parse_args()
    
    if args.action == "list":
        list_all_chunks()
    else:  # export
        export_chunks(args.output) 