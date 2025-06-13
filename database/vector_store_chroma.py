import uuid
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from .vector_store_base import VectorStoreBase

class ChromaVectorStore(VectorStoreBase):
    """ChromaDB implementation of vector store."""
    
    def __init__(self, 
                collection_name: str = "pdf_chunks",
                db_path: str = "./chroma_db",
                embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                **kwargs):
        """Initialize ChromaDB client and collection.
        
        Args:
            collection_name: Name of the collection
            db_path: Path to store ChromaDB files
            embedding_model: Model to use for embeddings
        """
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Set up embedding function
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_func
        )
    
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in ChromaDB.
        
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
            # Generate unique IDs for chunks
            ids = [str(uuid.uuid4()) for _ in chunks]
            
            # Add chunks to collection
            self.collection.add(
                documents=chunks,
                metadatas=metadata,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error storing chunks in ChromaDB: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in ChromaDB.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing search results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity score
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching in ChromaDB: {str(e)}")
            return []
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all stored chunks from ChromaDB.
        
        Returns:
            List of dictionaries containing all stored chunks
        """
        try:
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            formatted_results = []
            for i in range(len(results["ids"])):
                formatted_results.append({
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error retrieving chunks from ChromaDB: {str(e)}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a specific chunk by ID.
        
        Args:
            chunk_id: ID of the chunk to delete
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.collection.delete(ids=[chunk_id])
            return True
        except Exception as e:
            print(f"Error deleting chunk from ChromaDB: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all data in the collection.
        
        Returns:
            bool: True if clearing was successful
        """
        try:
            # Delete the collection if it exists
            if self.collection_name in self.client.list_collections():
                self.client.delete_collection(self.collection_name)
                
                # Recreate the collection
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_model
                )
            return True
        except Exception as e:
            print(f"Error clearing ChromaDB collection: {str(e)}")
            return False 