"""Test FAISS vector store functionality."""

import os
import shutil
from config.config import VECTOR_STORE_CONFIG
from database.vector_store_factory import create_vector_store

def test_faiss_basic_operations():
    """Test basic FAISS operations."""
    
    # Test data
    chunks = [
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing helps computers understand human language.",
        "Computer vision enables machines to interpret visual information."
    ]
    
    metadata = [
        {"source": "test1.pdf", "page": 1},
        {"source": "test2.pdf", "page": 1},
        {"source": "test3.pdf", "page": 1},
        {"source": "test4.pdf", "page": 1}
    ]
    
    # Clean up any existing index
    if os.path.exists("./faiss_index"):
        shutil.rmtree("./faiss_index")
    
    try:
        # Initialize vector store
        vector_store = create_vector_store(VECTOR_STORE_CONFIG)
        print("✅ Vector store initialized successfully")
        
        # Test storing chunks
        success = vector_store.store_chunks(chunks, metadata)
        assert success, "Failed to store chunks"
        print("✅ Stored chunks successfully")
        
        # Test search functionality
        results = vector_store.search("What is machine learning?", limit=2)
        assert len(results) > 0, "Search returned no results"
        print("\nSearch Results for 'What is machine learning?':")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Text: {result['text']}")
            print(f"   Source: {result['source']}")
            print(f"   Score: {result['score']}")
        
        # Test getting all chunks
        all_chunks = vector_store.get_all_chunks()
        assert len(all_chunks) == len(chunks), "Not all chunks were retrieved"
        print(f"\n✅ Retrieved all {len(all_chunks)} chunks successfully")
        
        # Test deleting a chunk
        first_chunk = vector_store.get_all_chunks()[0]
        chunk_id = first_chunk['metadata'].get('id', '0')
        success = vector_store.delete_chunk(str(chunk_id))
        assert success, "Failed to delete chunk"
        
        remaining_chunks = vector_store.get_all_chunks()
        assert len(remaining_chunks) == len(chunks) - 1, "Chunk was not deleted"
        print("✅ Deleted chunk successfully")
        
        # Test clearing collection
        success = vector_store.clear_collection()
        assert success, "Failed to clear collection"
        
        empty_chunks = vector_store.get_all_chunks()
        assert len(empty_chunks) == 0, "Collection was not cleared"
        print("✅ Cleared collection successfully")
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists("./faiss_index"):
            shutil.rmtree("./faiss_index")

if __name__ == "__main__":
    test_faiss_basic_operations() 