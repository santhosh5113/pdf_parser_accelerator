"""Weaviate vector store implementation."""

import json
import uuid
from typing import List, Dict, Any, Optional

import weaviate
import weaviate.classes as wvc
from sentence_transformers import SentenceTransformer
from weaviate.classes.config import Property, DataType, Configure
from weaviate.classes.data import DataObject

from .vector_store_base import VectorStoreBase

class WeaviateVectorStore(VectorStoreBase):
    """Vector store implementation using Weaviate."""
    
    def __init__(self, **kwargs):
        """Initialize Weaviate vector store for pipeline usage (v4+ client)."""
        super().__init__(**kwargs)
        self.collection_name = kwargs["collection_name"]
        self.embedding_model = SentenceTransformer(kwargs["embedding_model"])
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 8080)
        secure = kwargs.get("secure", False)
        if host == "localhost" and port == 8080 and not secure:
            self.client = weaviate.connect_to_local(skip_init_checks=True)
        else:
            self.client = weaviate.connect_to_custom(
                http_host=host,
                http_port=port,
                http_secure=secure,
                skip_init_checks=True
            )
        # Case-insensitive check for collection existence
        existing_collections = [c.lower() for c in self.client.collections.list_all()]
        if self.collection_name.lower() not in existing_collections:
            embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            self.client.collections.create(
                name=self.collection_name,
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="metadata_json", data_type=DataType.TEXT),
                ],
                vectorizer_config=[
                    Configure.NamedVectors.none(
                        name="custom_vector",
                        vector_index_config=Configure.VectorIndex.hnsw(
                            distance_metric=wvc.config.VectorDistances.COSINE,
                            vector_cache_max_objects=1000000,
                        )
                    )
                ]
            )
            print(f"✅ Created collection '{self.collection_name}' in Weaviate.")
        self.collection = self.client.collections.get(self.collection_name)
    
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in Weaviate."""
        if not chunks:
            print("ℹ️ No chunks to store")
            return True
        try:
            embeddings = self.embedding_model.encode(chunks)
            objects = []
            for text, embedding, meta in zip(chunks, embeddings, metadata):
                obj = {
                    "text": text,
                    "source": meta.get("source", "unknown"),
                    "metadata_json": json.dumps(meta)
                }
                objects.append(DataObject(properties=obj, vector=embedding.tolist()))
            self.collection.data.insert_many(objects)
            print(f"✅ Successfully stored in weaviate vector database")
            return True
        except Exception as e:
            print(f"❌ Error storing chunks in vector database: {e}")
            return False
    
    def search(self, query: str, limit: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in Weaviate."""
        try:
            if self.collection_name not in self.client.collections.list_all():
                print(f"Collection '{self.collection_name}' does not exist")
                return []
            query_embedding = self.embedding_model.encode(query)
            results = self.collection.query.near_vector(
                vector=query_embedding.tolist(),
                limit=limit,
                return_properties=["text", "source", "metadata_json"]
            )
            formatted = []
            for obj in results.objects:
                meta = json.loads(obj.properties["metadata_json"])
                formatted.append({
                    "text": obj.properties["text"],
                    "metadata": meta,
                    "score": obj.distance,
                    "source": obj.properties["source"]
                })
            return formatted
        except Exception as e:
            print(f"Error searching in Weaviate: {str(e)}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection."""
        try:
            # Case-insensitive check for collection existence
            existing_collections = [c.lower() for c in self.client.collections.list_all()]
            if self.collection_name.lower() in existing_collections:
                self.client.collections.delete(self.collection_name)
            embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            self.client.collections.create(
                name=self.collection_name,
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="metadata_json", data_type=DataType.TEXT),
                ],
                vectorizer_config=[
                    Configure.NamedVectors.none(
                        name="custom_vector",
                        vector_index_config=Configure.VectorIndex.hnsw(
                            distance_metric=wvc.config.VectorDistances.COSINE,
                            vector_cache_max_objects=1000000,
                        )
                    )
                ]
            )
            print(f"✅ Created collection '{self.collection_name}' in Weaviate.")
            self.collection = self.client.collections.get(self.collection_name)
            return True
        except Exception as e:
            print(f"Error clearing Weaviate collection: {str(e)}")
            return False
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all chunks from the collection."""
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
        """Delete a chunk from the collection."""
        try:
            self.collection.data.delete_by_id(chunk_id)
            return True
        except Exception as e:
            print(f"Error deleting chunk from Weaviate: {str(e)}")
            return False
    
    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass 