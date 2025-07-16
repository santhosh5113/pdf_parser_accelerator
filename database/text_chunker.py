"""Utility module for text chunking."""

import json
from typing import List, Dict, Any, Union
from transformers import AutoTokenizer
from config.vector_store_config import CHUNK_CONFIG
from .vector_store_factory import VectorStoreFactory
import re

# Initialize the HuggingFace tokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Add import for LangChain's RecursiveCharacterTextSplitter
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

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
    """Extract text content from different JSON formats, including LandingAI page_map format."""
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
        
        # --- LandingAI page_map format ---
        # All keys are page numbers, values are lists of dicts with 'captions'
        if all(isinstance(v, list) and all(isinstance(chunk, dict) for chunk in v) for v in data.values()):
            for page_chunks in data.values():
                for chunk in page_chunks:
                    captions = chunk.get('captions', [])
                    if isinstance(captions, list):
                        text_parts.extend([str(c) for c in captions if c])
                    elif isinstance(captions, str):
                        text_parts.append(captions)
            return "\n\n".join(text_parts)

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

def table_grid_to_markdown(grid):
    """Convert a Docling table grid to Markdown table string."""
    if not grid or not isinstance(grid, list):
        return ""
    # Extract header row (first row)
    header = [cell.get("text", "") for cell in grid[0]]
    # Extract all rows
    rows = [[cell.get("text", "") for cell in row] for row in grid]
    # Markdown formatting
    md = "| " + " | ".join(header) + " |\n"
    md += "| " + " | ".join(["---"] * len(header)) + " |\n"
    for row in rows[1:]:
        md += "| " + " | ".join(row) + " |\n"
    return md

def extract_blocks_from_json(data: Union[Dict, List, str]) -> List[Dict[str, str]]:
    """
    Extracts blocks from JSON, leveraging explicit table tags if present.
    Supports LlamaParse, Docling, LandingAI, and fallback formats.
    Returns a list of dicts: {"type": "table"|"text", "content": ...}
    """
    blocks = []
    # --- LandingAI page_map extraction ---
    if isinstance(data, dict) and all(isinstance(v, list) and all(isinstance(chunk, dict) for chunk in v) for v in data.values()):
        for page_chunks in data.values():
            for chunk in page_chunks:
                captions = chunk.get('captions', [])
                chunk_type = chunk.get('chunk_type', 'text')
                if isinstance(captions, list):
                    for caption in captions:
                        if caption:
                            blocks.append({"type": chunk_type, "content": str(caption)})
                elif isinstance(captions, str) and captions:
                    blocks.append({"type": chunk_type, "content": captions})
        return blocks
    # --- Docling extraction: add all texts as text blocks ---
    if isinstance(data, dict) and "texts" in data and isinstance(data["texts"], list):
        for text_entry in data["texts"]:
            if isinstance(text_entry, dict) and "text" in text_entry:
                blocks.append({"type": "text", "content": text_entry["text"]})
    # --- Docling table extraction ---
    if isinstance(data, dict) and "tables" in data and isinstance(data["tables"], list):
        for table in data["tables"]:
            # Try to use grid for Markdown
            grid = table.get("data", {}).get("grid")
            if grid:
                table_md = table_grid_to_markdown(grid)
                if table_md:
                    blocks.append({"type": "table", "content": table_md})
            else:
                # Fallback: join all cell texts
                cells = table.get("data", {}).get("table_cells", [])
                cell_texts = [cell.get("text", "") for cell in cells]
                if cell_texts:
                    blocks.append({"type": "table", "content": "\n".join(cell_texts)})
    # --- LlamaParse/other 'items' format ---
    elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        for item in data["items"]:
            if item.get("type") == "table":
                table_content = item.get("md") or item.get("csv") or str(item.get("rows", ""))
                if table_content:
                    blocks.append({"type": "table", "content": table_content})
            elif item.get("type") == "text":
                text_content = item.get("value", "")
                if text_content:
                    blocks.append({"type": "text", "content": text_content})
            elif item.get("type") == "heading":
                heading_content = item.get("value", "")
                if heading_content:
                    blocks.append({"type": "text", "content": heading_content})
    else:
        # Fallback: treat as a single text block
        blocks.append({"type": "text", "content": extract_text_from_json(data)})
    return blocks

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

def hybrid_chunk_text(text: str, max_tokens: int = None, overlap: int = None, min_chunk_chars: int = 100) -> List[Dict[str, str]]:
    if max_tokens is None:
        max_tokens = CHUNK_CONFIG["max_tokens"]
    if overlap is None:
        overlap = CHUNK_CONFIG["overlap"]

    # Improved: Group table blocks as a whole
    blocks = []
    current = []
    in_table = False
    lines = text.splitlines()
    for line in lines:
        if is_table_block(line):
            if not in_table:
                if current:
                    blocks.append(("text", "\n".join(current)))
                    current = []
                in_table = True
            current.append(line)
        else:
            if in_table:
                blocks.append(("table", "\n".join(current)))
                current = []
                in_table = False
            current.append(line)
    if current:
        blocks.append(("table" if in_table else "text", "\n".join(current)))

    # Now process each block
    chunks = []
    for block_type, block_content in blocks:
        if block_type == "table":
            # Only add if the table block is not too small
            if len(block_content.strip()) >= min_chunk_chars:
                chunks.append({"type": "table", "content": block_content.strip()})
        else:
            # Use RecursiveCharacterTextSplitter for text
            if _HAS_LANGCHAIN:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=max_tokens,
                    chunk_overlap=overlap,
                    separators=["\n\n", "\n", ".", "!", "?", " ", ""]
                )
                rec_chunks = splitter.split_text(block_content)
                for rec_chunk in rec_chunks:
                    if len(rec_chunk.strip()) >= min_chunk_chars:
                        chunks.append({"type": "text", "content": rec_chunk.strip()})
            else:
                # Fallback: Split by sentences, then by tokens
                sentences = re.split(r'(?<=[.!?])\s+', block_content)
                for sent in sentences:
                    if not sent.strip():
                        continue
                    tokens = tokenizer.encode(sent, add_special_tokens=False)
                    if len(tokens) > max_tokens:
                        start = 0
                        while start < len(tokens):
                            end = min(start + max_tokens, len(tokens))
                            chunk = tokenizer.decode(tokens[start:end])
                            if chunk.strip():
                                chunks.append({"type": "text", "content": chunk})
                            start += max_tokens - overlap
                    else:
                        chunks.append({"type": "text", "content": sent.strip()})
    return chunks

def hybrid_chunk_blocks(blocks, max_tokens=None, overlap=None, min_chunk_chars=100):
    if max_tokens is None:
        max_tokens = CHUNK_CONFIG["max_tokens"]
    if overlap is None:
        overlap = CHUNK_CONFIG["overlap"]
    chunks = []
    for block in blocks:
        block_type = block["type"]
        block_content = block["content"]
        if block_type == "table":
            if len(block_content.strip()) >= min_chunk_chars:
                chunks.append({"type": "table", "content": block_content.strip()})
        else:
            if _HAS_LANGCHAIN:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=max_tokens,
                    chunk_overlap=overlap,
                    separators=["\n\n", "\n", ".", "!", "?", " ", ""]
                )
                rec_chunks = splitter.split_text(block_content)
                for rec_chunk in rec_chunks:
                    if len(rec_chunk.strip()) >= min_chunk_chars:
                        chunks.append({"type": "text", "content": rec_chunk.strip()})
            else:
                sentences = re.split(r'(?<=[.!?])\s+', block_content)
                for sent in sentences:
                    if not sent.strip():
                        continue
                    tokens = tokenizer.encode(sent, add_special_tokens=False)
                    if len(tokens) > max_tokens:
                        start = 0
                        while start < len(tokens):
                            end = min(start + max_tokens, len(tokens))
                            chunk = tokenizer.decode(tokens[start:end])
                            if chunk.strip() and len(chunk.strip()) >= min_chunk_chars:
                                chunks.append({"type": "text", "content": chunk})
                            start += max_tokens - overlap
                    else:
                        if len(sent.strip()) >= min_chunk_chars:
                            chunks.append({"type": "text", "content": sent.strip()})
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

def process_pdf_json(json_path: str, source_id: str, vector_store_config: Dict[str, Any], chunk_size: int = 512, chunk_overlap: int = 64, min_chunk_chars: int = 0) -> bool:
    print(f"✅ Loading JSON from: {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("📄 JSON structure:")
        if "texts" in data:
            print(f"  - texts: {len(data['texts'])}")
        if "items" in data:
            print(f"  - items: {len(data['items'])}")
        if "tables" in data:
            print(f"  - tables: {len(data['tables'])}")
        if isinstance(data, dict) and len(data) == 1 and isinstance(list(data.values())[0], list):
            print(f"  - blocks: {len(list(data.values())[0])}")
        # Extract blocks using the enhanced logic
        blocks = extract_blocks_from_json(data)
        print(f"📝 Extracted {len(blocks)} blocks from JSON")
        # Hybrid chunking: tables as a whole, text split, but do not omit any chunk
        chunks = []
        chunk_index = 0
        for block in blocks:
            block_type = block.get("type", "text")
            content = block.get("content", "")
            # Apply hybrid chunking to each block
            split_chunks = hybrid_chunk_text(content, max_tokens=chunk_size, overlap=chunk_overlap)
            for split_chunk in split_chunks:
                chunk = {
                    "id": f"{source_id}_chunk_{chunk_index}",
                    "text": split_chunk["content"],
                    "metadata": {
                        "chunk_index": chunk_index,
                        "source": source_id,
                        "chunk_type": split_chunk.get("type", block_type),
                    }
                }
                chunks.append(chunk)
                chunk_index += 1
        print(f"✅ Created {len(chunks)} chunks (no filtering by size)")
        # Store chunks in the vector store
        store = VectorStoreFactory.create(vector_store_config)
        # ChromaVectorStore expects store_chunks(chunks, metadata)
        chunk_texts = [chunk["text"] for chunk in chunks]
        chunk_metadata = [chunk["metadata"] for chunk in chunks]
        store.store_chunks(chunk_texts, chunk_metadata)
        print(f"✅ Stored {len(chunks)} chunks in vector DB")
        return True
    except Exception as e:
        print(f"❌ Error processing PDF JSON: {e}")
        return False 