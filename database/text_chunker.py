"""Utility module for text chunking."""

import json
from typing import List, Dict, Any, Union
from transformers import AutoTokenizer
from config.vector_store_config import CHUNK_CONFIG
from .vector_store_factory import VectorStoreFactory

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
        
        # Chunk the text
        chunks = chunk_text(full_text)
        print(f"✅ Chunked into {len(chunks)} segments.")
        
        if not chunks:
            print("❌ No text chunks generated")
            return False
        
        # Prepare metadata for each chunk
        metadata = []
        for i in range(len(chunks)):
            metadata.append({
                "source": source_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "file_path": json_path
            })
        
        # Store chunks in vector database
        try:
            vector_store = VectorStoreFactory.create(vector_store_config)
            success = vector_store.store_chunks(chunks, metadata)
            return success
        except Exception as e:
            print(f"❌ Error storing chunks in vector database: {str(e)}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_path}: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Error processing JSON: {str(e)}")
        return False 