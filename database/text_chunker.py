"""Utility module for text chunking."""

import json
from typing import List, Dict, Any, Union
from transformers import AutoTokenizer
from config.vector_store_config import CHUNK_CONFIG
from .vector_store_factory import VectorStoreFactory
import re

# Initialize the HuggingFace tokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text: str) -> List[str]:
    """Chunk text using tokenizer with configured settings.
    
    Args:
        text: Text to chunk
    
    Returns:
        List of text chunks
    """
    # Skip empty or whitespace-only text
    if not text.strip():
        return []
        
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = min(start + CHUNK_CONFIG["max_tokens"], len(tokens))
        chunk = tokenizer.decode(tokens[start:end])
        # Skip empty chunks
        if chunk.strip():
            chunks.append(chunk)
        start += CHUNK_CONFIG["max_tokens"] - CHUNK_CONFIG["overlap"]
    
    return chunks

def resolve_references(data: Dict[str, Any], ref_path: str) -> Any:
    """Resolve JSON references in Docling format.
    
    Args:
        data: Full JSON document
        ref_path: Reference path (e.g., '#/texts/0')
        
    Returns:
        Resolved content
    """
    if not ref_path.startswith('#/'):
        return None
        
    parts = ref_path[2:].split('/')  # Remove '#/' and split
    current = data
    
    for part in parts:
        if part.isdigit():
            part = int(part)
        if isinstance(current, (dict, list)) and part in current:
            current = current[part]
        else:
            return None
            
    return current

def extract_text_from_json(data: Union[Dict, List, str]) -> str:
    """Extract text content from different JSON formats.
    
    Args:
        data: JSON data in various formats
        
    Returns:
        Extracted text content
    """
    if isinstance(data, str):
        return data
    
    if isinstance(data, list):
        # Handle list format (e.g., from vision parser)
        text_parts = []
        for item in data:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                # Try different possible key names
                for key in ['content', 'text', 'value', 'data']:
                    if key in item:
                        text_parts.append(str(item[key]))
                        break
        return "\n\n".join(text_parts)
    
    if isinstance(data, dict):
        text_parts = []
        
        # Handle Docling format - direct text entries
        if 'texts' in data and isinstance(data['texts'], list):
            for text_entry in data['texts']:
                if isinstance(text_entry, dict) and 'text' in text_entry:
                    text_parts.append(text_entry['text'])
        
        # Handle Docling format - references
        if 'body' in data and isinstance(data['body'], dict):
            body = data['body']
            if 'children' in body and isinstance(body['children'], list):
                for child in body['children']:
                    if isinstance(child, dict) and '$ref' in child:
                        ref = child['$ref']
                        if ref.startswith('#/texts/'):
                            resolved = resolve_references(data, ref)
                            if isinstance(resolved, dict) and 'text' in resolved:
                                text_parts.append(resolved['text'])
        
        # Handle direct text content
        for key in ['content', 'text', 'value', 'data']:
            if key in data:
                text_parts.append(str(data[key]))
        
        # Handle pages array (PDFMiner format)
        if 'pages' in data:
            pages = data['pages']
            if isinstance(pages, list):
                for page in pages:
                    if isinstance(page, str):
                        text_parts.append(page)
                    elif isinstance(page, dict):
                        # Handle PDFMiner format
                        if 'texts' in page:
                            page_texts = [text['text'] for text in page['texts'] if isinstance(text, dict) and 'text' in text]
                            text_parts.extend(page_texts)
                        # Handle PaddleOCR format
                        elif 'results' in page:
                            results = page['results']
                            if isinstance(results, list):
                                for result in results:
                                    if isinstance(result, dict) and 'text' in result:
                                        text_parts.append(str(result['text']))
                        # Handle other page formats
                        else:
                            status = page.get('status', page.get('success', True))
                            if status:
                                for key in ['content', 'text', 'value', 'data']:
                                    if key in page:
                                        text_parts.append(str(page[key]))
                                        break
        
        # Handle PaddleOCR format at root level
        if 'results' in data:
            results = data['results']
            if isinstance(results, list):
                for result in results:
                    if isinstance(result, dict) and 'text' in result:
                        text_parts.append(str(result['text']))
        
        return "\n\n".join(filter(None, text_parts))
    
    return ""

def process_pdf_json(json_path: str, source_id: str, vector_store_config: Dict[str, Any]) -> bool:
    """Process PDF JSON file and store chunks in vector database.
    
    Args:
        json_path: Path to JSON file containing parsed PDF content
        source_id: Identifier for the source document
        vector_store_config: Configuration for the vector store
    
    Returns:
        bool: True if processing was successful
    """
    print(f"✅ Loading JSON from: {json_path}")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Debug: Print JSON structure
        print("📄 JSON structure:")
        if "texts" in data:
            print(f"Found {len(data['texts'])} text entries")
            
        # Extract text from any JSON format
        full_text = extract_text_from_json(data)
        print(f"📝 Extracted text length: {len(full_text)}")
        if full_text:
            print("📝 First 200 characters of extracted text:")
            print(full_text[:200])
        
        # Hybrid chunking
        hybrid_chunks = hybrid_chunk_text(full_text)
        print(f"✅ Hybrid chunked into {len(hybrid_chunks)} segments.")
        print(f"Chunk types: {[chunk['type'] for chunk in hybrid_chunks[:10]]} ...")
        
        # Flatten for embedding/storage
        chunks = flatten_hybrid_chunks(hybrid_chunks)
        
        if not chunks:
            print("❌ No text chunks generated")
            return False
        
        # Prepare metadata for each chunk (include chunk type)
        metadata = []
        for i, chunk in enumerate(hybrid_chunks):
            metadata.append({
                "source": source_id,
                "chunk_index": i,
                "total_chunks": len(hybrid_chunks),
                "file_path": json_path,
                "chunk_type": chunk["type"]
            })
        
        # Store chunks in vector database
        try:
            vector_store = VectorStoreFactory.create(vector_store_config)
            vector_store.store_chunks(chunks, metadata)
            return True
        except Exception as e:
            print(f"❌ Error storing chunks in vector database: {str(e)}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_path}: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Error processing JSON: {str(e)}")
        return False

def is_table(element):
    # If your element is a dict/object, check for a 'type' field or structure
    if isinstance(element, dict) and element.get("type") == "table":
        return True
    # If it's a string, use heuristics
    table_keywords = ['table', 'row', 'column', 'cell']
    if isinstance(element, str) and any(word in element.lower() for word in table_keywords):
        # You can improve this with regex or structure checks
        return True
    return False

def table_aware_chunking(elements, max_tokens=512, overlap=50):
    chunks = []
    buffer = ""
    for elem in elements:
        if is_table(elem):
            # Flush buffer as a chunk before adding the table
            if buffer.strip():
                chunks.extend(tokenizer_based_chunking(buffer, max_tokens, overlap))
                buffer = ""
            # Add the table as a single chunk (stringify if needed)
            chunks.append({"type": "table", "content": str(elem)})
        else:
            buffer += elem if isinstance(elem, str) else str(elem)
            buffer += "\n"
    # Chunk any remaining buffer
    if buffer.strip():
        chunks.extend(tokenizer_based_chunking(buffer, max_tokens, overlap))
    return chunks

def tokenizer_based_chunking(text, max_tokens, overlap):
    # Use your existing chunk_text logic here
    return [{"type": "text", "content": chunk} for chunk in chunk_text(text)]

def is_table_block(text_block):
    # Heuristic 1: Table keywords
    table_keywords = ['table', 'row', 'column', 'cell', 'header']
    if any(word in text_block.lower() for word in table_keywords):
        return True

    # Heuristic 2: Delimiter-based (pipes or tabs)
    lines = text_block.strip().split('\n')
    if len(lines) > 1:
        # Check for consistent number of pipes or tabs
        pipe_counts = [line.count('|') for line in lines]
        tab_counts = [line.count('\t') for line in lines]
        if len(set(pipe_counts)) == 1 and pipe_counts[0] > 1:
            return True
        if len(set(tab_counts)) == 1 and tab_counts[0] > 1:
            return True

    # Heuristic 3: ASCII-art table
    if re.search(r'^\s*\+-[-+]+\+\s*$', text_block, re.MULTILINE):
        return True

    # Heuristic 4: Multiple columns with spaces
    if len(lines) > 1:
        col_counts = [len(re.split(r'\s{2,}', line)) for line in lines]
        if len(set(col_counts)) == 1 and col_counts[0] > 1:
            return True

        return False

def hybrid_chunk_text(text: str, max_tokens: int = None, overlap: int = None) -> List[Dict[str, str]]:
    """
    Hybrid chunking: splits text into tables and non-table blocks, preserves tables, splits long blocks recursively.
    Args:
        text: The full text to chunk.
        max_tokens: Max tokens per chunk (defaults to CHUNK_CONFIG["max_tokens"])
        overlap: Overlap tokens between chunks (defaults to CHUNK_CONFIG["overlap"])
    Returns:
        List of dicts: {"type": "text"|"table", "content": ...}
    """
    if max_tokens is None:
        max_tokens = CHUNK_CONFIG["max_tokens"]
    if overlap is None:
        overlap = CHUNK_CONFIG["overlap"]

    # Split text into blocks (tables vs. non-tables)
    blocks = []
    current = []
    lines = text.splitlines()
    for line in lines:
        if is_table_block(line):
            if current:
                blocks.append(("text", "\n".join(current)))
                current = []
            blocks.append(("table", line))
        else:
            current.append(line)
    if current:
        blocks.append(("text", "\n".join(current)))

    # Now process each block
    chunks = []
    for block_type, block_content in blocks:
        if block_type == "table":
            chunks.append({"type": "table", "content": block_content})
        else:
            # Split by paragraphs (double newlines)
            paragraphs = [p for p in re.split(r'\n\s*\n', block_content) if p.strip()]
            for para in paragraphs:
                # If paragraph is too long, split by sentences
                if len(tokenizer.encode(para, add_special_tokens=False)) > max_tokens:
                    # Split by sentences (simple split, can use nltk for better)
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        if not sent.strip():
                            continue
                        # Recursively split if still too long
                        tokens = tokenizer.encode(sent, add_special_tokens=False)
                        if len(tokens) > max_tokens:
                            # Token-based split
                            start = 0
                            while start < len(tokens):
                                end = min(start + max_tokens, len(tokens))
                                chunk = tokenizer.decode(tokens[start:end])
                                if chunk.strip():
                                    chunks.append({"type": "text", "content": chunk})
                                start += max_tokens - overlap
                        else:
                            chunks.append({"type": "text", "content": sent.strip()})
                else:
                    chunks.append({"type": "text", "content": para.strip()})
    return chunks


def flatten_hybrid_chunks(hybrid_chunks: List[Dict[str, str]]) -> List[str]:
    """
    Flattens hybrid chunk output to just text chunks (for embedding).
    Args:
        hybrid_chunks: Output from hybrid_chunk_text
    Returns:
        List of text chunks (tables and text as plain text)
    """
    return [chunk["content"] for chunk in hybrid_chunks] 