"""Factory for creating vector store instances."""

from typing import Dict, Any
from .vector_store_base import VectorStoreBase

class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    @staticmethod
    def create(config: Dict[str, Any]) -> 'VectorStoreBase':
        """Create a vector store instance based on configuration.
        
        Args:
            config: Configuration dictionary with:
                - type: Type of vector store (chroma, qdrant, weaviate, milvus, faiss, pinecone)
                - Other type-specific configuration
                
        Returns:
            VectorStoreBase: Configured vector store instance
        
        Raises:
            ValueError: If vector store type is not supported
        """
        store_type = config.get("type", "").lower()
        
        if store_type == "chroma":
            from .vector_store_chroma import ChromaVectorStore
            return ChromaVectorStore(**config)
            
        elif store_type == "qdrant":
            from .vector_store_qdrant import QdrantVectorStore
            return QdrantVectorStore(**config)
            
        elif store_type == "weaviate":
            from .vector_store_weaviate import WeaviateVectorStore
            return WeaviateVectorStore(**config)
            
        elif store_type == "milvus":
            from .vector_store_milvus import MilvusVectorStore
            return MilvusVectorStore(**config)
            
        elif store_type == "faiss":
            from .vector_store_faiss import FaissVectorStore
            return FaissVectorStore(**config)
        elif store_type == "pinecone":
            from .vector_store_pinecone import PineconeVectorStore
            return PineconeVectorStore(**config)
            
        else:
            raise ValueError(f"Unknown vector store type: {store_type}") 