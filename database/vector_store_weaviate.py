"""Weaviate vector store implementation."""

import json
import uuid
from typing import List, Dict, Any, Optional

import weaviate
from sentence_transformers import SentenceTransformer

from .vector_store_base import VectorStoreBase

class WeaviateVectorStore(VectorStoreBase):
    """Vector store implementation using Weaviate."""
    
    def __init__(self, **kwargs):
        """Initialize Weaviate vector store.
        
        Args:
            **kwargs: Configuration arguments including:
                - collection_name: Name of the collection/class in Weaviate
                - embedding_model: Name of the HuggingFace model to use for embeddings
                - url: Weaviate server URL (default: http://localhost:8080)
        """
        super().__init__(**kwargs)
        
        # Store configuration
        self.collection_name = kwargs["collection_name"]
        self.embedding_model = SentenceTransformer(kwargs["embedding_model"])
        
        # Initialize Weaviate client
        self.client = weaviate.Client(
            url=kwargs.get("url", "http://localhost:8080")
        )
        
        # Create class if it doesn't exist
        if not self.client.schema.exists(self.collection_name):
            class_obj = {
                "class": self.collection_name,
                "vectorizer": "none",  # We'll provide vectors explicitly
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"]
                    },
                    {
                        "name": "source",
                        "dataType": ["string"]
                    },
                    {
                        "name": "metadata_json",
                        "dataType": ["text"]
                    }
                ]
            }
            self.client.schema.create_class(class_obj)
    
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in Weaviate.
        
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
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks)
            
            # Prepare objects for batch import
            with self.client.batch as batch:
                for text, embedding, meta in zip(chunks, embeddings, metadata):
                    # Create unique ID
                    doc_uuid = str(uuid.uuid4())
                    
                    # Convert metadata to JSON string
                    metadata_json = json.dumps(meta)
                    
                    # Prepare properties
                    properties = {
                        "text": text,
                        "source": meta.get("source", "unknown"),
                        "metadata_json": metadata_json
                    }
                    
                    # Add object with vector
                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.collection_name,
                        uuid=doc_uuid,
                        vector=embedding.tolist()
                    )
            
            return True
            
        except Exception as e:
            print(f"Error storing chunks in Weaviate: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in Weaviate.
        
        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            **kwargs: Additional arguments
            
        Returns:
            List of results with text, metadata and score
        """
        try:
            # Check if class exists
            if not self.client.schema.exists(self.collection_name):
                print(f"Collection '{self.collection_name}' does not exist")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search in Weaviate
            result = (
                self.client.query
                .get(self.collection_name, ["text", "source", "metadata_json", "_additional {certainty}"])
                .with_near_vector({
                    "vector": query_embedding.tolist()
                })
                .with_limit(limit)
                .do()
            )
            
            # Extract results
            hits = result["data"]["Get"].get(self.collection_name, [])
            if not hits:
                return []
            
            # Format results
            results = []
            for hit in hits:
                # Parse metadata JSON
                metadata = json.loads(hit["metadata_json"])
                
                results.append({
                    "text": hit["text"],
                    "metadata": metadata,
                    "score": hit["_additional"]["certainty"],
                    "source": hit["source"]
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching in Weaviate: {str(e)}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection.
        
        Returns:
            bool: True if clearing was successful
        """
        try:
            if self.client.schema.exists(self.collection_name):
                self.client.schema.delete_class(self.collection_name)
                
                # Recreate the class
                class_obj = {
                    "class": self.collection_name,
                    "vectorizer": "none",
                    "properties": [
                        {
                            "name": "text",
                            "dataType": ["text"]
                        },
                        {
                            "name": "source",
                            "dataType": ["string"]
                        },
                        {
                            "name": "metadata_json",
                            "dataType": ["text"]
                        }
                    ]
                }
                self.client.schema.create_class(class_obj)
            return True
        except Exception as e:
            print(f"Error clearing Weaviate collection: {str(e)}")
            return False
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all chunks from the collection.
        
        Returns:
            List of all chunks with their metadata
        """
        try:
            result = (
                self.client.query
                .get(self.collection_name, ["text", "source", "metadata_json"])
                .do()
            )
            
            hits = result["data"]["Get"][self.collection_name]
            return [
                {
                    "text": hit["text"],
                    "metadata": json.loads(hit["metadata_json"]),
                    "source": hit["source"]
                }
                for hit in hits
            ]
        except Exception as e:
            print(f"Error getting chunks from Weaviate: {str(e)}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from the collection.
        
        Args:
            chunk_id: ID of the chunk to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.client.data_object.delete(
                uuid=chunk_id,
                class_name=self.collection_name
            )
            return True
        except Exception as e:
            print(f"Error deleting chunk from Weaviate: {str(e)}")
            return False 