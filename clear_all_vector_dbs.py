from database.vector_store_factory import VectorStoreFactory
from config.vector_store_config import CHROMA_CONFIG, QDRANT_CONFIG, WEAVIATE_CONFIG, MILVUS_CONFIG, FAISS_CONFIG, PINECONE_CONFIG
import os

vector_db_configs = [
    CHROMA_CONFIG,
    QDRANT_CONFIG,
    WEAVIATE_CONFIG,
    MILVUS_CONFIG,
    FAISS_CONFIG,
    PINECONE_CONFIG,
]

def main():
    for config in vector_db_configs:
        db_type = config.get("type", "unknown")
        print(f"\nClearing {db_type} vector DB...")
        # Warn if Pinecone API key is not set
        if db_type == "pinecone":
            api_key = config.get("api_key")
            if not api_key or api_key.startswith("<YOUR_"):
                print("[WARNING] Pinecone API key not set. Skipping Pinecone.")
                continue
        try:
            store = VectorStoreFactory.create(config)
            result = store.clear_collection()
            if result:
                print(f"[SUCCESS] Cleared {db_type} vector DB.")
            else:
                print(f"[FAIL] Could not clear {db_type} vector DB.")
        except Exception as e:
            print(f"[ERROR] Exception clearing {db_type}: {e}")

if __name__ == "__main__":
    main() 