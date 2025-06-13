import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from .vector_store_base import VectorStoreBase
import uuid
import os

class PineconeVectorStore(VectorStoreBase):
    """Pinecone implementation of vector store."""

    def __init__(self, 
                 api_key: str,
                 environment: str,
                 index_name: str = "pdf_chunks",
                 collection_name: str = "pdf_chunks",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 **kwargs):
        """Initialize Pinecone client and index."""
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = index_name
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(embedding_model)

        pinecone.init(api_key=self.api_key, environment=self.environment)
        if self.index_name not in pinecone.list_indexes():
            # Create index if it doesn't exist
            dim = self.embedding_model.get_sentence_embedding_dimension()
            pinecone.create_index(self.index_name, dimension=dim)
        self.index = pinecone.Index(self.index_name)

    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in Pinecone."""
        if not chunks:
            print("ℹ️ No chunks to store")
            return True
        try:
            embeddings = self.embedding_model.encode(chunks)
            vectors = []
            for i, (embedding, text, meta) in enumerate(zip(embeddings, chunks, metadata)):
                vector_id = str(uuid.uuid4())
                vectors.append((vector_id, embedding.tolist(), {"text": text, "metadata": meta}))
            self.index.upsert(vectors)
            return True
        except Exception as e:
            print(f"Error storing chunks in Pinecone: {str(e)}")
            return False

    def search(self, query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in Pinecone."""
        try:
            query_embedding = self.embedding_model.encode([query])[0]
            results = self.index.query(queries=[query_embedding.tolist()], top_k=limit, include_metadata=True)
            matches = results['results'][0]['matches'] if results['results'] else []
            formatted_results = []
            for match in matches:
                formatted_results.append({
                    "id": match["id"],
                    "text": match["metadata"].get("text", ""),
                    "metadata": match["metadata"].get("metadata", {}),
                    "score": match["score"]
                })
            return formatted_results
        except Exception as e:
            print(f"Error searching in Pinecone: {str(e)}")
            return []

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all stored chunks from Pinecone (limited by API)."""
        try:
            # Pinecone does not support listing all vectors directly; this is a placeholder
            print("Pinecone does not support fetching all vectors directly via API.")
            return []
        except Exception as e:
            print(f"Error retrieving chunks from Pinecone: {str(e)}")
            return []

    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a specific chunk by ID."""
        try:
            self.index.delete(ids=[chunk_id])
            return True
        except Exception as e:
            print(f"Error deleting chunk from Pinecone: {str(e)}")
            return False

    def clear_collection(self) -> bool:
        """Delete all data in the index."""
        try:
            self.index.delete(delete_all=True)
            return True
        except Exception as e:
            print(f"Error clearing Pinecone index: {str(e)}")
            return False 