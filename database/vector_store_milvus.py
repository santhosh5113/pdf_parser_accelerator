"""Milvus vector store implementation."""

import json
from typing import List, Dict, Any, Optional

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from sentence_transformers import SentenceTransformer

from .vector_store_base import VectorStoreBase

class MilvusVectorStore(VectorStoreBase):
    """Vector store implementation using Milvus."""
    
    def __init__(self, **kwargs):
        """Initialize Milvus vector store.
        
        Args:
            **kwargs: Configuration arguments including:
                - collection_name: Name of the collection in Milvus
                - embedding_model: Name of the HuggingFace model to use for embeddings
                - host: Milvus server host (default: localhost)
                - port: Milvus server port (default: 19530)
        """
        super().__init__(**kwargs)
        
        # Store configuration
        self.collection_name = kwargs["collection_name"]
        self.embedding_model = SentenceTransformer(kwargs["embedding_model"])
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 19530)
        
        # Connect to Milvus
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )
        
        # Create collection if it doesn't exist
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists with the correct schema."""
        # Define fields
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="metadata_json", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)  # Dimension from all-MiniLM-L6-v2
        ]
        
        # Create schema
        schema = CollectionSchema(
            fields=fields,
            description="PDF chunks collection"
        )
        
        # Create collection if it doesn't exist
        if not utility.has_collection(self.collection_name):
            collection = Collection(name=self.collection_name, schema=schema)
            
            # Create IVF_FLAT index for vector field
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="vector", index_params=index_params)
    
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in Milvus.
        
        Args:
            chunks: List of text chunks to store
            metadata: List of metadata dictionaries for each chunk
            **kwargs: Additional arguments
            
        Returns:
            bool: True if storage was successful
        """
        # Skip if no chunks
        if not chunks:
            print("ℹ️ No chunks to store")
            return True
            
        try:
            # Get collection
            collection = Collection(self.collection_name)
            
            # Convert chunks to strings if they're lists
            processed_chunks = []
            for chunk in chunks:
                if isinstance(chunk, list):
                    # If chunk is a list of strings, join them
                    if all(isinstance(item, str) for item in chunk):
                        chunk = " ".join(chunk)
                    # If chunk is a list of dicts, extract text values
                    elif all(isinstance(item, dict) for item in chunk):
                        text_parts = []
                        for item in chunk:
                            for key in ['text', 'content', 'value', 'data']:
                                if key in item:
                                    text_parts.append(str(item[key]))
                                    break
                        chunk = " ".join(text_parts)
                    else:
                        # If we can't process it, convert to string
                        chunk = str(chunk)
                processed_chunks.append(str(chunk))  # Ensure all chunks are strings
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(processed_chunks)
            
            # Prepare data
            data = [
                {
                    "text": chunk,
                    "source": meta.get("source", "unknown"),
                    "metadata_json": json.dumps(meta),
                    "vector": embedding.tolist()
                }
                for chunk, meta, embedding in zip(processed_chunks, metadata, embeddings)
            ]
            
            # Insert data
            collection.insert(data)
            collection.flush()
            
            return True
            
        except Exception as e:
            print(f"Error storing chunks in Milvus: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in Milvus.
        
        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            **kwargs: Additional arguments
            
        Returns:
            List of results with text, metadata and score
        """
        try:
            # Get collection
            collection = Collection(self.collection_name)
            
            # Load collection
            collection.load()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search parameters
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            # Search
            results = collection.search(
                data=[query_embedding.tolist()],
                anns_field="vector",
                param=search_params,
                limit=limit,
                output_fields=["text", "source", "metadata_json"]
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    # Parse metadata JSON
                    metadata = json.loads(hit.entity.get("metadata_json"))
                    
                    formatted_results.append({
                        "text": hit.entity.get("text"),
                        "metadata": metadata,
                        "score": float(hit.score),
                        "source": hit.entity.get("source")
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching in Milvus: {str(e)}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all data in the collection.
        
        Returns:
            bool: True if clearing was successful
        """
        try:
            # Drop collection if it exists
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                
                # Recreate collection
                self._ensure_collection()
            return True
        except Exception as e:
            print(f"Error clearing Milvus collection: {str(e)}")
            return False
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all chunks from the collection.
        
        Returns:
            List of all chunks with their metadata
        """
        try:
            # Get collection
            collection = Collection(self.collection_name)
            
            # Load collection
            collection.load()
            
            # Query all data
            results = collection.query(
                expr="id >= 0",  # Match all documents
                output_fields=["text", "source", "metadata_json"]
            )
            
            # Format results
            formatted_results = []
            for hit in results:
                # Parse metadata JSON
                metadata = json.loads(hit["metadata_json"])
                
                formatted_results.append({
                    "text": hit["text"],
                    "metadata": metadata,
                    "source": hit["source"]
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error getting chunks from Milvus: {str(e)}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from the collection.
        
        Args:
            chunk_id: ID of the chunk to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Get collection
            collection = Collection(self.collection_name)
            
            # Delete chunk
            collection.delete(f"id == {chunk_id}")
            collection.flush()
            
            return True
        except Exception as e:
            print(f"Error deleting chunk from Milvus: {str(e)}")
            return False 