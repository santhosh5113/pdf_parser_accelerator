from chromadb import PersistentClient
import json

def export_chunks_to_file(output_path="exported_chunks.json"):
    client = PersistentClient(path="./chroma_persist")
    collection = client.get_collection(name="pdf_chunks")

    # ✅ FIX: Only include supported keys
    results = collection.get(include=["documents", "metadatas"])

    exported = []

    # ✅ ids are always returned even if not in include
    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        exported.append({
            "id": doc_id,
            "content": doc,
            "source": meta.get("source", "unknown")
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(exported, f, indent=2, ensure_ascii=False)

    print(f"✅ Exported {len(exported)} chunks to '{output_path}'")

if __name__ == "__main__":
    export_chunks_to_file()
