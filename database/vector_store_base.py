"""Base class for vector database implementations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStoreBase(ABC):
    """Base class for vector database implementations."""
    
    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize the vector store with configuration."""
        pass
    
    @abstractmethod
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata.
        
        Args:
            chunks: List of text chunks to store
            metadata: List of metadata dictionaries for each chunk
            **kwargs: Additional arguments
            
        Returns:
            bool: True if storage was successful
        """
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks.
        
        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            **kwargs: Additional arguments
            
        Returns:
            List of results with text, metadata and score
        """
        pass
    
    @abstractmethod
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all stored chunks.
        
        Returns:
            List of all chunks with their metadata
        """
        pass
    
    @abstractmethod
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a specific chunk by ID.
        
        Args:
            chunk_id: ID of the chunk to delete
            
        Returns:
            bool: True if deletion was successful
        """
        pass
    
    @abstractmethod
    def clear_collection(self) -> bool:
        """Clear all data in the collection.
        
        Returns:
            bool: True if clearing was successful
        """
        pass 