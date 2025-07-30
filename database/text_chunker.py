"""Utility module for text chunking with hybrid table-aware chunking."""

import json
import re
from typing import List, Dict, Any, Union, Tuple
from transformers import AutoTokenizer
from config.vector_store_config import CHUNK_CONFIG
from .vector_store_factory import VectorStoreFactory

# Initialize the HuggingFace tokenizer
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")

# Add import for LangChain's RecursiveCharacterTextSplitter
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    raise ImportError("LangChain is required for chunking. Please install langchain.")

def table_grid_to_markdown(grid):
    """Convert a Docling table grid to Markdown table string."""
    if not grid or not isinstance(grid, list):
        return ""
    header = [cell.get("text", "") for cell in grid[0]]
    rows = [[cell.get("text", "") for cell in row] for row in grid]
    md = "| " + " | ".join(header) + " |\n"
    md += "| " + " | ".join(["---"] * len(header)) + " |\n"
    for row in rows[1:]:
        md += "| " + " | ".join(row) + " |\n"
    return md

def is_table_content(content: str) -> bool:
    """Detect if content is a table based on various indicators."""
    if not content:
        return False
    
    # Check for HTML table tags
    if re.search(r'<table[^>]*>.*?</table>', content, re.DOTALL | re.IGNORECASE):
        return True
    
    # Check for markdown table format
    if re.search(r'\|.*\|.*\n\|.*---.*\|', content, re.MULTILINE):
        return True
    
    # Check for CSV-like structure with commas and consistent columns
    lines = content.strip().split('\n')
    if len(lines) >= 2:
        # Check if first line has consistent comma separation
        first_line_parts = [part.strip() for part in lines[0].split(',')]
        if len(first_line_parts) >= 3:  # At least 3 columns
            # Check if subsequent lines have similar structure
            consistent_structure = True
            for line in lines[1:3]:  # Check next 2 lines
                if line.strip():
                    line_parts = [part.strip() for part in line.split(',')]
                    if len(line_parts) != len(first_line_parts):
                        consistent_structure = False
                        break
            if consistent_structure:
                return True
    
    # Check for tabular data with consistent spacing
    if re.search(r'\s{2,}', content):  # Multiple spaces indicating tabular format
        lines = content.strip().split('\n')
        if len(lines) >= 3:
            # Check if lines have consistent column structure
            first_line_columns = len(re.findall(r'\s{2,}', lines[0])) + 1
            consistent = True
            for line in lines[1:3]:
                if line.strip():
                    line_columns = len(re.findall(r'\s{2,}', line)) + 1
                    if line_columns != first_line_columns:
                        consistent = False
                        break
            if consistent and first_line_columns >= 3:
                return True
    
    return False

def extract_blocks_from_json(data: Union[Dict, List, str], chunk_size, chunk_overlap, min_chunk_chars) -> List[Dict[str, str]]:
    """
    Extracts blocks from JSON, leveraging explicit table tags if present.
    Supports LlamaParse, Docling, LandingAI, PyMuPDF, and fallback/manual formats.
    Returns a list of dicts: {"type": "table"|"text", "content": ...}
    
    Args:
        data: JSON data from parser
        chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between chunks
        min_chunk_chars: Minimum characters per chunk
    """
    blocks = []
    
    # --- PyMuPDF extraction ---
    if isinstance(data, dict) and "text_by_page" in data and "text_with_coordinates" in data:
        # Extract text by page (simpler approach)
        text_by_page = data.get("text_by_page", {})
        for page_num, page_text in text_by_page.items():
            if page_text and page_text.strip():
                # Check if page content looks like a table
                actual_type = "table" if is_table_content(page_text) else "text"
                
                if actual_type == "table":
                    # Keep tables as single blocks
                    blocks.append({
                        "type": actual_type, 
                        "content": page_text.strip(),
                        "page": int(page_num),
                        "parser": "pymupdf"
                    })
                else:
                    # Apply chunking during extraction using character-based parameters
                    text_chunks = chunk_text_during_extraction(page_text.strip(), chunk_size, chunk_overlap, min_chunk_chars)
                    for i, text_chunk in enumerate(text_chunks):
                        blocks.append({
                            "type": actual_type, 
                            "content": text_chunk,
                            "page": int(page_num),
                            "chunk_index": i,
                            "total_chunks": len(text_chunks),
                            "parser": "pymupdf"
                        })
        
        # If no text found in text_by_page, try text_with_coordinates
        if not blocks:
            text_with_coords = data.get("text_with_coordinates", {})
            for page_num, text_blocks in text_with_coords.items():
                if isinstance(text_blocks, list):
                    # Group text blocks by proximity and font characteristics
                    page_content = []
                    current_paragraph = []
                    last_y = None
                    last_font_size = None
                    
                    for block in text_blocks:
                        if isinstance(block, dict):
                            text = block.get("text", "").strip()
                            bbox = block.get("bbox", [])
                            font_size = block.get("size", 0)
                            
                            if text:
                                # Check if this block should start a new paragraph
                                should_new_paragraph = False
                                if last_y is not None and bbox:
                                    y_diff = abs(bbox[1] - last_y)
                                    # If significant vertical gap or font size change, new paragraph
                                    if y_diff > 20 or (last_font_size and abs(font_size - last_font_size) > 2):
                                        should_new_paragraph = True
                                
                                if should_new_paragraph and current_paragraph:
                                    page_content.append(" ".join(current_paragraph))
                                    current_paragraph = []
                                
                                current_paragraph.append(text)
                                last_y = bbox[1] if bbox else None
                                last_font_size = font_size
                    
                    # Add the last paragraph
                    if current_paragraph:
                        page_content.append(" ".join(current_paragraph))
                    
                    # Join paragraphs with double newlines
                    full_page_text = "\n\n".join(page_content)
                    if full_page_text.strip():
                        actual_type = "table" if is_table_content(full_page_text) else "text"
                        
                        if actual_type == "table":
                            # Keep tables as single blocks
                            blocks.append({
                                "type": actual_type,
                                "content": full_page_text.strip(),
                                "page": int(page_num),
                                "parser": "pymupdf"
                            })
                        else:
                            # Apply chunking during extraction using character-based parameters
                            text_chunks = chunk_text_during_extraction(full_page_text.strip(), chunk_size, chunk_overlap, min_chunk_chars)
                            for i, text_chunk in enumerate(text_chunks):
                                blocks.append({
                                    "type": actual_type,
                                    "content": text_chunk,
                                    "page": int(page_num),
                                    "chunk_index": i,
                                    "total_chunks": len(text_chunks),
                                    "parser": "pymupdf"
                                })
        
        return blocks
    
    # --- LandingAI page_map extraction ---
    if isinstance(data, dict) and all(isinstance(v, list) and all(isinstance(chunk, dict) for chunk in v) for v in data.values()):
        prev_content = None
        for page_chunks in data.values():
            for chunk in page_chunks:
                captions = chunk.get('captions', [])
                chunk_type = chunk.get('chunk_type', 'text')
                if isinstance(captions, list):
                    for caption in captions:
                        if caption:
                            # Override chunk_type if content looks like a table
                            actual_type = "table" if is_table_content(str(caption)) else chunk_type
                            
                            if actual_type == "table":
                                # Keep tables as single blocks
                                blocks.append({"type": actual_type, "content": str(caption)})
                                # Reset prev_content for tables - don't include table content in overlap
                                prev_content = None
                            else:
                                # Smart chunking: only apply character-level chunking if content is too large
                                if len(str(caption)) > chunk_size:
                                    # Apply chunking for oversized blocks
                                    text_chunks = chunk_text_during_extraction(str(caption), chunk_size, chunk_overlap, min_chunk_chars)
                                    for i, text_chunk in enumerate(text_chunks):
                                        blocks.append({
                                            "type": actual_type, 
                                            "content": text_chunk,
                                            "chunk_index": i,
                                            "total_chunks": len(text_chunks),
                                            "parser": "landingai"
                                        })
                                else:
                                    # Add chunk overlap from previous content if available
                                    if prev_content is not None and chunk_overlap > 0:
                                        overlap = prev_content[-chunk_overlap:]
                                        overlapped_content = overlap + str(caption)
                                    else:
                                        overlapped_content = str(caption)
                                    blocks.append({
                                        "type": actual_type, 
                                        "content": overlapped_content,
                                        "parser": "landingai",
                                        "chunking_strategy": "parser_natural_with_overlap"
                                    })
                                    prev_content = str(caption)
                elif isinstance(captions, str) and captions:
                    actual_type = "table" if is_table_content(captions) else chunk_type
                    
                    if actual_type == "table":
                        # Keep tables as single blocks
                        blocks.append({"type": actual_type, "content": captions})
                        # Reset prev_content for tables - don't include table content in overlap
                        prev_content = None
                    else:
                        # Smart chunking: only apply character-level chunking if content is too large
                        if len(captions) > chunk_size:
                            # Apply chunking for oversized blocks
                            text_chunks = chunk_text_during_extraction(captions, chunk_size, chunk_overlap, min_chunk_chars)
                            for i, text_chunk in enumerate(text_chunks):
                                blocks.append({
                                    "type": actual_type, 
                                    "content": text_chunk,
                                    "chunk_index": i,
                                    "total_chunks": len(text_chunks),
                                    "parser": "landingai"
                                })
                        else:
                            # Add chunk overlap from previous content if available
                            if prev_content is not None and chunk_overlap > 0:
                                overlap = prev_content[-chunk_overlap:]
                                overlapped_content = overlap + captions
                            else:
                                overlapped_content = captions
                            blocks.append({
                                "type": actual_type, 
                                "content": overlapped_content,
                                "parser": "landingai",
                                "chunking_strategy": "parser_natural_with_overlap"
                            })
                            prev_content = captions
        return blocks
    
    # --- Docling extraction: add all texts as text blocks ---
    if isinstance(data, dict) and "texts" in data and isinstance(data["texts"], list):
        prev_content = None
        for text_entry in data["texts"]:
            if isinstance(text_entry, dict) and "text" in text_entry:
                content = text_entry["text"]
                actual_type = "table" if is_table_content(content) else "text"
                
                if actual_type == "table":
                    # Keep tables as single blocks
                    blocks.append({"type": actual_type, "content": content})
                    # Reset prev_content for tables - don't include table content in overlap
                    prev_content = None
                else:
                    # Smart chunking: only apply character-level chunking if content is too large
                    if len(content) > chunk_size:
                        # Apply chunking for oversized blocks
                        text_chunks = chunk_text_during_extraction(content, chunk_size, chunk_overlap, min_chunk_chars)
                        for i, text_chunk in enumerate(text_chunks):
                            blocks.append({
                                "type": actual_type, 
                                "content": text_chunk,
                                "chunk_index": i,
                                "total_chunks": len(text_chunks),
                                "parser": "docling"
                            })
                    else:
                        # Add chunk overlap from previous paragraph if available
                        if prev_content is not None and chunk_overlap > 0:
                            overlap = prev_content[-chunk_overlap:]
                            overlapped_content = overlap + content
                        else:
                            overlapped_content = content
                        blocks.append({
                            "type": actual_type, 
                            "content": overlapped_content,
                            "parser": "docling",
                            "chunking_strategy": "parser_natural_with_overlap"
                        })
                        prev_content = content
    
    # --- Docling table extraction ---
    if isinstance(data, dict) and "tables" in data and isinstance(data["tables"], list):
        for table in data["tables"]:
            grid = table.get("data", {}).get("grid")
            if grid:
                table_md = table_grid_to_markdown(grid)
                if table_md:
                    # Apply chunking to large tables
                    if len(table_md) > chunk_size:
                        text_chunks = chunk_text_during_extraction(table_md, chunk_size, chunk_overlap, min_chunk_chars)
                        for i, text_chunk in enumerate(text_chunks):
                            blocks.append({
                                "type": "table", 
                                "content": text_chunk,
                                "chunk_index": i,
                                "total_chunks": len(text_chunks),
                                "parser": "docling"
                            })
                    else:
                        blocks.append({"type": "table", "content": table_md})
            else:
                cells = table.get("data", {}).get("table_cells", [])
                cell_texts = [cell.get("text", "") for cell in cells]
                if cell_texts:
                    table_content = "\n".join(cell_texts)
                    # Apply chunking to large tables
                    if len(table_content) > chunk_size:
                        text_chunks = chunk_text_during_extraction(table_content, chunk_size, chunk_overlap, min_chunk_chars)
                        for i, text_chunk in enumerate(text_chunks):
                            blocks.append({
                                "type": "table", 
                                "content": text_chunk,
                                "chunk_index": i,
                                "total_chunks": len(text_chunks),
                                "parser": "docling"
                            })
                    else:
                        blocks.append({"type": "table", "content": table_content})
    
    # --- LlamaParse/other 'items' format ---
    elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        prev_content = None
        for item in data["items"]:
            if item.get("type") == "table":
                # Prefer markdown, then html, then csv, then rows
                table_content = item.get("md") or item.get("html") or item.get("csv") or str(item.get("rows", ""))
                if table_content:
                    blocks.append({"type": "table", "content": table_content})
                    # Reset prev_content for tables - don't include table content in overlap
                    prev_content = None
            elif item.get("type") == "text":
                text_content = item.get("value", "")
                if text_content:
                    actual_type = "table" if is_table_content(text_content) else "text"
                    
                    if actual_type == "table":
                        # Keep tables as single blocks
                        blocks.append({"type": actual_type, "content": text_content})
                        # Reset prev_content for tables - don't include table content in overlap
                        prev_content = None
                    else:
                        # Smart chunking: only apply character-level chunking if content is too large
                        if len(text_content) > chunk_size:
                            # Apply chunking for oversized blocks
                            text_chunks = chunk_text_during_extraction(text_content, chunk_size, chunk_overlap, min_chunk_chars)
                            for i, text_chunk in enumerate(text_chunks):
                                blocks.append({
                                    "type": actual_type, 
                                    "content": text_chunk,
                                    "chunk_index": i,
                                    "total_chunks": len(text_chunks),
                                    "parser": "llamaparse"
                                })
                        else:
                            # Add chunk overlap from previous content if available
                            if prev_content is not None and chunk_overlap > 0:
                                overlap = prev_content[-chunk_overlap:]
                                overlapped_content = overlap + text_content
                            else:
                                overlapped_content = text_content
                            blocks.append({
                                "type": actual_type, 
                                "content": overlapped_content,
                                "parser": "llamaparse",
                                "chunking_strategy": "parser_natural_with_overlap"
                            })
                            prev_content = text_content
            elif item.get("type") == "heading":
                heading_content = item.get("value", "")
                if heading_content:
                    # Smart chunking for headings: only apply character-level chunking if content is too large
                    if len(heading_content) > chunk_size:
                        # Apply chunking for oversized headings
                        text_chunks = chunk_text_during_extraction(heading_content, chunk_size, chunk_overlap, min_chunk_chars)
                        for i, text_chunk in enumerate(text_chunks):
                            blocks.append({
                                "type": "text", 
                                "content": text_chunk,
                                "chunk_index": i,
                                "total_chunks": len(text_chunks),
                                "parser": "llamaparse"
                            })
                    else:
                        # Add chunk overlap from previous content if available
                        if prev_content is not None and chunk_overlap > 0:
                            overlap = prev_content[-chunk_overlap:]
                            overlapped_content = overlap + heading_content
                        else:
                            overlapped_content = heading_content
                        blocks.append({
                            "type": "text", 
                            "content": overlapped_content,
                            "parser": "llamaparse",
                            "chunking_strategy": "parser_natural_with_overlap"
                        })
                        prev_content = heading_content
    
    # --- LlamaParse with 'pages' format ---
    elif isinstance(data, dict) and "pages" in data and isinstance(data["pages"], list):
        prev_content = None
        for page in data["pages"]:
            # Handle 'items' in each page
            if isinstance(page, dict) and "items" in page and isinstance(page["items"], list):
                for item in page["items"]:
                    if item.get("type") == "table":
                        table_content = item.get("md") or item.get("html") or item.get("csv") or str(item.get("rows", ""))
                        if table_content:
                            blocks.append({"type": "table", "content": table_content})
                            # Reset prev_content for tables - don't include table content in overlap
                            prev_content = None
                    elif item.get("type") == "text":
                        text_content = item.get("value", "")
                        if text_content:
                            actual_type = "table" if is_table_content(text_content) else "text"
                            
                            if actual_type == "table":
                                # Keep tables as single blocks
                                blocks.append({"type": actual_type, "content": text_content})
                                # Reset prev_content for tables - don't include table content in overlap
                                prev_content = None
                            else:
                                # Smart chunking: only apply character-level chunking if content is too large
                                if len(text_content) > chunk_size:
                                    # Apply chunking for oversized blocks
                                    text_chunks = chunk_text_during_extraction(text_content, chunk_size, chunk_overlap, min_chunk_chars)
                                    for i, text_chunk in enumerate(text_chunks):
                                        blocks.append({
                                            "type": actual_type, 
                                            "content": text_chunk,
                                            "chunk_index": i,
                                            "total_chunks": len(text_chunks),
                                            "parser": "llamaparse"
                                        })
                                else:
                                    # Add chunk overlap from previous content if available
                                    if prev_content is not None and chunk_overlap > 0:
                                        overlap = prev_content[-chunk_overlap:]
                                        overlapped_content = overlap + text_content
                                    else:
                                        overlapped_content = text_content
                                    blocks.append({
                                        "type": actual_type, 
                                        "content": overlapped_content,
                                        "parser": "llamaparse",
                                        "chunking_strategy": "parser_natural_with_overlap"
                                    })
                                    prev_content = text_content
                    elif item.get("type") == "heading":
                        heading_content = item.get("value", "")
                        if heading_content:
                            # Smart chunking for headings: only apply character-level chunking if content is too large
                            if len(heading_content) > chunk_size:
                                # Apply chunking for oversized headings
                                text_chunks = chunk_text_during_extraction(heading_content, chunk_size, chunk_overlap, min_chunk_chars)
                                for i, text_chunk in enumerate(text_chunks):
                                    blocks.append({
                                        "type": "text", 
                                        "content": text_chunk,
                                        "chunk_index": i,
                                        "total_chunks": len(text_chunks),
                                        "parser": "llamaparse"
                                    })
                            else:
                                # Add chunk overlap from previous content if available
                                if prev_content is not None and chunk_overlap > 0:
                                    overlap = prev_content[-chunk_overlap:]
                                    overlapped_content = overlap + heading_content
                                else:
                                    overlapped_content = heading_content
                                blocks.append({
                                    "type": "text", 
                                    "content": overlapped_content,
                                    "parser": "llamaparse",
                                    "chunking_strategy": "parser_natural_with_overlap"
                                })
                                prev_content = heading_content
            
            # Handle direct text content in pages
            elif isinstance(page, dict) and "text" in page:
                text_content = page["text"]
                if text_content:
                    actual_type = "table" if is_table_content(text_content) else "text"
                    
                    if actual_type == "table":
                        # Keep tables as single blocks
                        blocks.append({"type": actual_type, "content": text_content})
                        # Reset prev_content for tables - don't include table content in overlap
                        prev_content = None
                    else:
                        # Smart chunking: only apply character-level chunking if content is too large
                        if len(text_content) > chunk_size:
                            # Apply chunking for oversized blocks
                            text_chunks = chunk_text_during_extraction(text_content, chunk_size, chunk_overlap, min_chunk_chars)
                            for i, text_chunk in enumerate(text_chunks):
                                blocks.append({
                                    "type": actual_type, 
                                    "content": text_chunk,
                                    "chunk_index": i,
                                    "total_chunks": len(text_chunks),
                                    "parser": "llamaparse"
                                })
                        else:
                            # Add chunk overlap from previous content if available
                            if prev_content is not None and chunk_overlap > 0:
                                overlap = prev_content[-chunk_overlap:]
                                overlapped_content = overlap + text_content
                            else:
                                overlapped_content = text_content
                            blocks.append({
                                "type": actual_type, 
                                "content": overlapped_content,
                                "parser": "llamaparse",
                                "chunking_strategy": "parser_natural_with_overlap"
                            })
                            prev_content = text_content
    
    # --- Fallback: treat as plain text ---
    elif isinstance(data, str):
        actual_type = "table" if is_table_content(data) else "text"
        
        if actual_type == "table":
            # Keep tables as single blocks
            blocks.append({"type": actual_type, "content": data})
        else:
            # Apply chunking during extraction using character-based parameters
            text_chunks = chunk_text_during_extraction(data, chunk_size, chunk_overlap, min_chunk_chars)
            for i, text_chunk in enumerate(text_chunks):
                blocks.append({
                    "type": actual_type, 
                    "content": text_chunk,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "parser": "fallback"
                })
    
    return blocks

def chunk_text_during_extraction(text: str, chunk_size, chunk_overlap, min_chunk_chars) -> List[str]:
    """
    Chunk text during extraction to ensure all parsers follow size constraints.
    Uses character-based chunking with configurable size and overlap.
    This is applied directly during block extraction, not just during hybrid_chunk_blocks.
    """
    assert chunk_size is not None and chunk_overlap is not None and min_chunk_chars is not None, "Chunking parameters must be provided explicitly!"

    if not text or len(text.strip()) == 0:
        return []
    
    # If text is small enough, return as is
    if len(text.strip()) < min_chunk_chars:
        return [text.strip()] if text.strip() else []
    
    # Check if text is already within character limits
    text_chars = len(text.strip())
    if text_chars <= chunk_size:
        return [text.strip()]
    
    # Apply chunking for large texts using character-based parameters
    chunks = chunk_text_recursive(text, chunk_size, chunk_overlap)
    
    # Filter chunks by minimum size after chunking
    valid_chunks = [chunk for chunk in chunks if len(chunk) >= min_chunk_chars]
    
    # If no valid chunks after splitting, keep the original if it meets minimum
    if not valid_chunks and len(text.strip()) >= min_chunk_chars:
        return [text.strip()]
    
    return valid_chunks



def chunk_text_recursive(text: str, chunk_size, chunk_overlap) -> List[str]:
    """Chunk text using LangChain's RecursiveCharacterTextSplitter with character-based chunking."""
    assert chunk_size is not None and chunk_overlap is not None, "Chunking parameters must be provided explicitly!"

    if not text or len(text.strip()) == 0:
        return []
    
    # Initialize the text splitter with character-based chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,  # Use character count for splitting
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    
    # Split the text
    chunks = text_splitter.split_text(text)
    
    # Post-process chunks to ensure they don't exceed character limits
    validated_chunks = []
    for chunk in chunks:
        chunk_chars = len(chunk.strip())
        if chunk_chars <= chunk_size:
            validated_chunks.append(chunk.strip())
        else:
            # If chunk is too large, split it manually by sentences
            print(f"⚠️ Warning: Chunk exceeded {chunk_size} characters ({chunk_chars} characters), splitting manually...")
            sentences = chunk.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                test_chunk = current_chunk + sentence + ". "
                if len(test_chunk) <= chunk_size:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        validated_chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                validated_chunks.append(current_chunk.strip())
    
    return [chunk for chunk in validated_chunks if chunk.strip()]

def hybrid_chunk_blocks(blocks: List[Dict[str, str]], chunk_size, chunk_overlap, min_chunk_chars) -> List[Dict[str, str]]:
    """
    Apply hybrid chunking: keep tables as single chunks, split text recursively.
    Uses character-based chunking with configurable size and overlap.
    
    Args:
        blocks: List of blocks with type and content
        chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between chunks
        min_chunk_chars: Minimum characters per chunk
    
    Returns:
        List of chunked blocks with metadata
    """
    chunked_blocks = []
    
    for i, block in enumerate(blocks):
        block_type = block.get("type", "text")
        content = block.get("content", "").strip()
        
        if not content:
            continue
        
        if block_type == "table":
            # Keep tables as single chunks (regardless of size)
            table_chars = len(content)
            print(f"📋 Table block {i}: {table_chars} characters (kept as single chunk)")
            chunked_blocks.append({
                "type": "table",
                "content": content,
                "original_block_index": i,
                "chunk_index": 0,
                "total_chunks": 1,
                "table_size_chars": table_chars
            })
        else:
            # Check if this block was already processed during extraction (either chunked or with overlap)
            if "chunk_index" in block and "total_chunks" in block:
                # Block was already chunked during extraction, just add it
                chunked_blocks.append({
                    "type": "text",
                    "content": content,
                    "original_block_index": i,
                    "chunk_index": block.get("chunk_index", 0),
                    "total_chunks": block.get("total_chunks", 1),
                    "parser": block.get("parser", "unknown")
                })
            elif "chunking_strategy" in block:
                # Block was processed with overlap during extraction, just add it
                chunked_blocks.append({
                    "type": "text",
                    "content": content,
                    "original_block_index": i,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "parser": block.get("parser", "unknown"),
                    "chunking_strategy": block.get("chunking_strategy", "unknown")
                })
            else:
                # For text blocks that weren't processed during extraction, apply chunking now
                # This ensures all parsers (Docling, LlamaParse, LandingAI) follow chunk constraints
                # Use character-based parameters
                text_chunks = chunk_text_recursive(content, chunk_size, chunk_overlap)
                
                # Filter chunks by minimum size after chunking
                valid_chunks = [chunk for chunk in text_chunks if len(chunk) >= min_chunk_chars]
                
                if valid_chunks:
                    for j, chunk in enumerate(valid_chunks):
                        chunked_blocks.append({
                            "type": "text",
                            "content": chunk,
                            "original_block_index": i,
                            "chunk_index": j,
                            "total_chunks": len(valid_chunks)
                        })
                else:
                    # If no valid chunks after splitting, keep the original if it meets minimum
                    if len(content) >= min_chunk_chars:
                        chunked_blocks.append({
                            "type": "text",
                            "content": content,
                            "original_block_index": i,
                            "chunk_index": 0,
                            "total_chunks": 1
                        })
    
    return chunked_blocks

def process_pdf_json_hybrid(json_path: str, source_id: str, vector_store_config: Dict[str, Any]) -> bool:
    """
    Process PDF JSON with hybrid chunking (table-aware).
    Uses hardcoded chunk size (1000 chars) and overlap (200 chars).
    
    Args:
        json_path: Path to the JSON file
        source_id: Source identifier
        vector_store_config: Vector store configuration
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract blocks from JSON with character-based chunking constraints
        blocks = extract_blocks_from_json(data, CHUNK_CONFIG["max_tokens"], CHUNK_CONFIG["overlap"], min_chunk_chars=CHUNK_CONFIG["min_tokens"])
        
        if not blocks:
            print(f"⚠️ No content blocks found in {json_path}")
            return False
        
        # Apply hybrid chunking with character-based parameters
        chunked_blocks = hybrid_chunk_blocks(blocks, CHUNK_CONFIG["max_tokens"], CHUNK_CONFIG["overlap"], min_chunk_chars=CHUNK_CONFIG["min_tokens"])
        
        if not chunked_blocks:
            print(f"⚠️ No chunks generated from {json_path}")
            return False
        
        # Prepare chunks for vector store
        chunks = []
        metadata_list = []
        
        for i, chunk_block in enumerate(chunked_blocks):
            chunk_text = chunk_block["content"]
            chunk_type = chunk_block["type"]
            
            # Create metadata
            metadata = {
                "source": source_id,
                "chunk_type": chunk_type,
                "chunk_index": i,
                "original_block_index": chunk_block.get("original_block_index", 0),
                "chunk_index_in_block": chunk_block.get("chunk_index", 0),
                "total_chunks_in_block": chunk_block.get("total_chunks", 1),
                "parser": chunk_block.get("parser", "hybrid_chunker")
            }
            
            # Add page number only if it's not None
            page_num = chunk_block.get("page")
            if page_num is not None:
                metadata["page"] = page_num
            
            # Clean metadata for ChromaDB compatibility
            cleaned_metadata = clean_metadata_for_chromadb(metadata)
            
            chunks.append(chunk_text)
            metadata_list.append(cleaned_metadata)
        
        # Store in vector database
        store = VectorStoreFactory.create(vector_store_config)
        success = store.store_chunks(chunks, metadata_list)
        
        if success:
            print(f"✅ Successfully processed {json_path}")
            print(f"   📊 Total blocks: {len(blocks)}")
            print(f"   📄 Total chunks: {len(chunks)}")
            print(f"   📋 Table chunks: {sum(1 for m in metadata_list if m['chunk_type'] == 'table')}")
            print(f"   📝 Text chunks: {sum(1 for m in metadata_list if m['chunk_type'] == 'text')}")
        else:
            print(f"❌ Failed to store chunks from {json_path}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error processing {json_path}: {str(e)}")
        return False

# Keep existing functions for backward compatibility
def is_table_block(text_block):
    """Check if a text block is a table."""
    return is_table_content(text_block)

def split_paragraphs_with_overlap(text, chunk_size, overlap):
    """Split text into paragraphs with overlap."""
    return chunk_text_recursive(text, chunk_size, overlap)

def hybrid_chunk_text(text: str, chunk_size, chunk_overlap, min_chunk_chars) -> List[Dict[str, str]]:
    """Legacy function - use hybrid_chunk_blocks instead."""
    # Detect if text is a table
    if is_table_content(text):
        return [{"type": "table", "content": text}]
    else:
        chunks = chunk_text_recursive(text, chunk_size, chunk_overlap)
        return [{"type": "text", "content": chunk} for chunk in chunks if len(chunk) >= min_chunk_chars]

def clean_metadata_for_chromadb(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean metadata to ensure compatibility with ChromaDB.
    ChromaDB only accepts: str, int, float, bool (not None)
    """
    cleaned_metadata = {}
    for key, value in metadata.items():
        if value is None:
            # Skip None values
            continue
        elif isinstance(value, (str, int, float, bool)):
            # These types are directly supported
            cleaned_metadata[key] = value
        else:
            # Convert other types to string
            cleaned_metadata[key] = str(value)
    return cleaned_metadata

def flatten_hybrid_chunks(hybrid_chunks: List[Dict[str, str]]) -> List[str]:
    """Flatten hybrid chunks to list of strings."""
    return [chunk["content"] for chunk in hybrid_chunks]

def process_pdf_json(json_path: str, source_id: str, vector_store_config: Dict[str, Any]) -> bool:
    """Process PDF JSON with hardcoded chunking (1000 chars, 200 overlap)."""
    return process_pdf_json_hybrid(json_path, source_id, vector_store_config) 
