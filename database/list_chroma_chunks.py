import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

def view_all_chunks():
    # Connect to the persistent ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")

    # Load the collection
    collection = client.get_or_create_collection(
        name="pdf_chunks",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )

    # Retrieve stored chunks (IDs are included by default)
    results = collection.get(include=["documents", "metadatas"])

    documents = results["documents"]
    ids = results["ids"]  # This is always returned, no need to request it
    metadatas = results["metadatas"]

    print(f"🧠 Found {len(documents)} chunks in 'pdf_chunks' collection.\n")

    for i in range(len(documents)):
        print(f"🔹 ID: {ids[i]}")
        print(f"📄 Document: {documents[i]}")
        print(f"📝 Metadata: {metadatas[i]}")
        print("-" * 50)

if __name__ == "__main__":
    view_all_chunks()
