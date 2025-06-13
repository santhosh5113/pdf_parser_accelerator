"""FAISS vector store implementation."""

import os
import json
import pickle
from typing import List, Dict, Any, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .vector_store_base import VectorStoreBase

class FaissVectorStore(VectorStoreBase):
    """Vector store implementation using FAISS."""
    
    def __init__(self, **kwargs):
        """Initialize FAISS vector store.
        
        Args:
            **kwargs: Configuration arguments including:
                - collection_name: Name of the collection (used for file naming)
                - embedding_model: Name of the HuggingFace model to use for embeddings
                - index_path: Path to store the FAISS index (default: ./faiss_index)
        """
        super().__init__(**kwargs)
        
        # Store configuration
        self.collection_name = kwargs["collection_name"]
        self.embedding_model = SentenceTransformer(kwargs["embedding_model"])
        self.index_path = kwargs.get("index_path", "./faiss_index")
        
        # Create index directory if it doesn't exist
        os.makedirs(self.index_path, exist_ok=True)
        
        # Initialize or load index
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index and metadata."""
        self.index_file = os.path.join(self.index_path, f"{self.collection_name}.index")
        self.meta_file = os.path.join(self.index_path, f"{self.collection_name}.meta")
        
        # Initialize metadata storage
        if os.path.exists(self.meta_file):
            with open(self.meta_file, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.metadata = []
        
        # Initialize or load index
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            # Create a new index - using L2 distance and IVF for fast search
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)  # Start with basic index
            
            # If we have enough data points, convert to IVF index
            if len(self.metadata) > 1000:
                nlist = min(len(self.metadata) // 10, 1000)  # Number of clusters
                quantizer = faiss.IndexFlatL2(dimension)
                self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                self.index.train(np.array(self._get_all_vectors()))
    
    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def _get_all_vectors(self) -> List[np.ndarray]:
        """Get all vectors from the index.
        
        Returns:
            List of vectors
        """
        if self.index.ntotal == 0:
            return []
        vectors = []
        for i in range(self.index.ntotal):
            vector = np.zeros((1, self.index.d), dtype=np.float32)
            self.index.reconstruct(i, vector[0])
            vectors.append(vector[0])
        return vectors
    
    def store_chunks(self, chunks: List[str], metadata: List[Dict[str, Any]], **kwargs) -> bool:
        """Store text chunks with their metadata in FAISS.
        
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
            
            # Convert to float32 for FAISS
            vectors = np.array(embeddings).astype('float32')
            
            # Add vectors to index
            self.index.add(vectors)
            
            # Store metadata
            start_idx = len(self.metadata)
            for i, meta in enumerate(metadata):
                meta['id'] = start_idx + i
                meta['text'] = processed_chunks[i]
                self.metadata.append(meta)
            
            # Save to disk
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error storing chunks in FAISS: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar chunks in FAISS.
        
        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            **kwargs: Additional arguments
            
        Returns:
            List of results with text, metadata and score
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Convert to float32 and reshape
            query_vector = np.array([query_embedding]).astype('float32')
            
            # Search
            distances, indices = self.index.search(query_vector, limit)
            
            # Format results
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0 or idx >= len(self.metadata):  # Skip invalid indices
                    continue
                    
                meta = self.metadata[idx]
                results.append({
                    "text": meta["text"],
                    "metadata": {k: v for k, v in meta.items() if k not in ["text", "id"]},
                    "score": float(dist),
                    "source": meta.get("source", "unknown")
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching in FAISS: {str(e)}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all data in the collection.
        
        Returns:
            bool: True if clearing was successful
        """
        try:
            # Reset index
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            
            # Reset metadata
            self.metadata = []
            
            # Save empty state
            self._save_index()
            
            return True
        except Exception as e:
            print(f"Error clearing FAISS collection: {str(e)}")
            return False
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all chunks from the collection.
        
        Returns:
            List of all chunks with their metadata
        """
        try:
            results = []
            for meta in self.metadata:
                results.append({
                    "text": meta["text"],
                    "metadata": {k: v for k, v in meta.items() if k not in ["text", "id"]},
                    "source": meta.get("source", "unknown")
                })
            return results
            
        except Exception as e:
            print(f"Error getting chunks from FAISS: {str(e)}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from the collection.
        
        Args:
            chunk_id: ID of the chunk to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Find chunk in metadata
            chunk_idx = None
            for i, meta in enumerate(self.metadata):
                if meta.get("id") == int(chunk_id):
                    chunk_idx = i
                    break
            
            if chunk_idx is None:
                print(f"Chunk with ID {chunk_id} not found")
                return False
            
            # Remove from metadata
            self.metadata.pop(chunk_idx)
            
            # Rebuild index with remaining vectors
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            new_index = faiss.IndexFlatL2(dimension)
            
            # Re-add all vectors except the deleted one
            chunks = [meta["text"] for meta in self.metadata]
            if chunks:
                embeddings = self.embedding_model.encode(chunks)
                vectors = np.array(embeddings).astype('float32')
                new_index.add(vectors)
            
            # Replace old index
            self.index = new_index
            
            # Save changes
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error deleting chunk from FAISS: {str(e)}")
            return False 