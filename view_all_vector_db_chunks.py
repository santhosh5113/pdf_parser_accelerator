from database.vector_store_factory import VectorStoreFactory
from config.vector_store_config import CHROMA_CONFIG, QDRANT_CONFIG, WEAVIATE_CONFIG, MILVUS_CONFIG, FAISS_CONFIG

vector_db_configs = [
    CHROMA_CONFIG,
    QDRANT_CONFIG,
    WEAVIATE_CONFIG,
    MILVUS_CONFIG,
    FAISS_CONFIG,
]

def main():
    for config in vector_db_configs:
        db_type = config.get("type", "unknown")
        print(f"\n--- {db_type.upper()} Vector DB ---")
        try:
            store = VectorStoreFactory.create(config)
            chunks = store.get_all_chunks()
            if not chunks:
                print("[INFO] No chunks found.")
            else:
                for i, chunk in enumerate(chunks, 1):
                    print(f"Chunk {i}: {chunk}")
        except Exception as e:
            print(f"[ERROR] Could not retrieve chunks from {db_type}: {e}")

if __name__ == "__main__":
    main() 