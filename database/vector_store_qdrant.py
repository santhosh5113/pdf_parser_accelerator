from typing import List, Dict, Any, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from .vector_store_base import VectorStoreBase

class QdrantVectorStore(VectorStoreBase):
    """Qdrant implementation of vector store."""
    
    def __init__(self, 
                 collection_name: str = "pdf_chunks",
                 location: str = ":memory:",  # Use ":memory:" for testing, URL for production
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 **kwargs):
        """Initialize Qdrant client and collection.
        
        Args:
            collection_name: Name of the collection to store vectors
            location: Location of Qdrant server (":memory:" or URL)
            embedding_model: Model to use for text embeddings
        """
        self.collection_name = collection_name
        self.client = QdrantClient(location=location)
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get vector size from model
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
        
        # Create collection if it doesn't exist
        self._create_collection()
        
        # Set up sparse model for hybrid search if specified
        if kwargs.get("use_sparse", False):
            self.client.set_sparse_model("Qdrant/bm25")
    
    def _create_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
    
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in Qdrant.
        
        Args:
            chunks: List of text chunks to store
            metadata: List of metadata dictionaries for each chunk
        
        Returns:
            bool: True if storage was successful
        """
        # Skip if no chunks
        if not chunks:
            print("ℹ️ No chunks to store")
            return True
        
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks)
            
            # Prepare points for insertion
            points = []
            for i, (embedding, text, meta) in enumerate(zip(embeddings, chunks, metadata)):
                point_id = str(uuid.uuid4())
                points.append(models.PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "text": text,
                        "metadata": meta
                    }
                ))
            
            # Insert points into collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            print(f"Error storing chunks in Qdrant: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in Qdrant.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing search results
        """
        try:
            # Generate query embedding
            query_vector = self.embedding_model.encode(query)
            
            # Search in collection
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit
            )
            
            # Format results
            formatted_results = []
            for res in results:
                formatted_results.append({
                    "id": res.id,
                    "text": res.payload["text"],
                    "metadata": res.payload["metadata"],
                    "score": res.score
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return []
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all stored chunks from Qdrant.
        
        Returns:
            List of dictionaries containing all stored chunks
        """
        try:
            # Scroll through all points in collection
            points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust based on your needs
            )[0]
            
            # Format results
            results = []
            for point in points:
                results.append({
                    "id": point.id,
                    "text": point.payload["text"],
                    "metadata": point.payload["metadata"]
                })
            
            return results
        except Exception as e:
            print(f"Error retrieving chunks: {str(e)}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a specific chunk by ID.
        
        Args:
            chunk_id: ID of the chunk to delete
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[chunk_id]
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting chunk: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all data in the collection.
        
        Returns:
            bool: True if clearing was successful
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._create_collection()
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False 