
import os
import uuid
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from transformers import AutoTokenizer
from typing import List

# Initialize the HuggingFace tokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Chunk text using tokenizer
def chunk_text(text: str, max_tokens: int = 256, overlap: int = 50) -> List[str]:
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = tokenizer.decode(tokens[start:end])
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks

# Store Markdown file content in Chroma vector DB
def store_pdf_chunks(md_path: str, source_id: str):
    print(f"✅ Loading Markdown from: {md_path}")
    
    with open(md_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    chunks = chunk_text(markdown_text)
    print(f"✅ Chunked into {len(chunks)} segments.")

    # Create a persistent Chroma client
    client = chromadb.PersistentClient(path="./chroma_db")

    # Use Chroma's default embedding function (you can also use OpenAI or custom)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create or get collection
    collection = client.get_or_create_collection(
        name="pdf_chunks", embedding_function=embedding_func
    )

    # Generate unique IDs for each chunk
    ids = [f"{source_id}_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]

    # Add chunks to Chroma
    collection.upsert(
        documents=chunks,
        ids=ids,
        metadatas=[{"source": source_id}] * len(chunks)
    )

    print(f"✅ Stored {len(chunks)} chunks in ChromaDB under collection 'pdf_chunks'.")

