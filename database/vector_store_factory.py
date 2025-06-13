"""Factory for creating vector store instances."""

from typing import Dict, Any
from .vector_store_base import VectorStoreBase
from .vector_store_qdrant import QdrantVectorStore
from .vector_store_chroma import ChromaVectorStore
from .vector_store_weaviate import WeaviateVectorStore
from .vector_store_milvus import MilvusVectorStore
from .vector_store_faiss import FaissVectorStore
from .vector_store_pinecone import PineconeVectorStore

class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    @staticmethod
    def create(config: Dict[str, Any]) -> VectorStoreBase:
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
            return ChromaVectorStore(**config)
            
        elif store_type == "qdrant":
            return QdrantVectorStore(**config)
            
        elif store_type == "weaviate":
            return WeaviateVectorStore(**config)
            
        elif store_type == "milvus":
            return MilvusVectorStore(**config)
            
        elif store_type == "faiss":
            return FaissVectorStore(**config)
        elif store_type == "pinecone":
            return PineconeVectorStore(**config)
            
        else:
            raise ValueError(f"Unknown vector store type: {store_type}") 