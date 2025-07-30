# Chunking Analysis: Inconsistencies Across Parsers

## Current Configuration
- **Chunk Size:** 1000 characters
- **Overlap:** 200 characters  
- **Min Chunk:** 100 characters

## Parser-by-Parser Analysis

### 1. **PyMuPDF** - ✅ MOSTLY CONSISTENT
**Logic:**
- Applies `chunk_text_during_extraction()` to text blocks
- Keeps tables as single blocks
- Uses character-based chunking with proper overlap

**Issues:**
- Early return in `chunk_text_during_extraction()` if text ≤ chunk_size
- This means pages smaller than 1000 chars are kept as single chunks
- **Inconsistency:** Small pages don't get chunked even if they exceed min_chunk_chars

### 2. **Docling** - ⚠️ INCONSISTENT OVERLAP
**Logic:**
- **Text blocks:** Smart chunking - only chunks if > chunk_size, otherwise adds overlap from previous
- **Tables:** Chunks if > chunk_size, otherwise keeps as single block

**Issues:**
- **Inconsistency:** Natural paragraph chunks get overlap, but character-chunked blocks don't
- **Inconsistency:** Tables can be chunked (unlike other parsers)
- **Inconsistency:** Overlap logic is different from other parsers

### 3. **LlamaParse** - ⚠️ INCONSISTENT OVERLAP
**Logic:**
- **Text blocks:** Smart chunking - only chunks if > chunk_size, otherwise adds overlap
- **Headings:** Same smart chunking logic
- **Tables:** Keeps as single blocks

**Issues:**
- **Inconsistency:** Same as Docling - natural chunks get overlap, character-chunked don't
- **Inconsistency:** Different overlap strategy from PyMuPDF

### 4. **LandingAI** - ⚠️ INCONSISTENT OVERLAP
**Logic:**
- **Text blocks:** Smart chunking - only chunks if > chunk_size, otherwise adds overlap
- **Tables:** Keeps as single blocks

**Issues:**
- **Inconsistency:** Same as Docling/LlamaParse
- **Inconsistency:** Different from PyMuPDF

### 5. **Fallback** - ✅ CONSISTENT
**Logic:**
- Applies `chunk_text_during_extraction()` to all text
- Keeps tables as single blocks

**Issues:**
- Same early return issue as PyMuPDF

## Key Inconsistencies

### 1. **Chunking Strategy Mismatch**
- **PyMuPDF & Fallback:** Always apply character-based chunking
- **Docling, LlamaParse, LandingAI:** Smart chunking (natural + overlap)

### 2. **Overlap Application**
- **PyMuPDF & Fallback:** Overlap only in character-chunked blocks
- **Docling, LlamaParse, LandingAI:** Overlap in natural chunks, no overlap in character-chunked

### 3. **Table Handling**
- **PyMuPDF & Fallback:** Never chunk tables
- **Docling:** Can chunk tables if > chunk_size
- **LlamaParse & LandingAI:** Never chunk tables

### 4. **Early Return Issue**
- **PyMuPDF & Fallback:** Skip chunking if text ≤ chunk_size
- **Docling, LlamaParse, LandingAI:** No early return, always apply smart logic

## Recommended Fixes

### Option 1: Standardize on Smart Chunking
Make all parsers use the same smart chunking logic:
- If content > chunk_size: Apply character-based chunking
- If content ≤ chunk_size: Keep natural chunks with overlap

### Option 2: Standardize on Always Chunk
Make all parsers always apply character-based chunking:
- Remove early return in `chunk_text_during_extraction()`
- Apply consistent overlap to all chunks

### Option 3: Hybrid Approach
- **Text:** Smart chunking for all parsers
- **Tables:** Never chunk (standardize across all parsers)
- **Overlap:** Consistent application across all chunking strategies

## Current State Summary

| Parser | Text Chunking | Table Chunking | Overlap Strategy | Consistency |
|--------|---------------|----------------|------------------|-------------|
| PyMuPDF | Always chunk | Never chunk | Character-based only | ⚠️ Early return issue |
| Docling | Smart chunking | Can chunk | Natural + overlap | ⚠️ Different strategy |
| LlamaParse | Smart chunking | Never chunk | Natural + overlap | ⚠️ Different strategy |
| LandingAI | Smart chunking | Never chunk | Natural + overlap | ⚠️ Different strategy |
| Fallback | Always chunk | Never chunk | Character-based only | ⚠️ Early return issue |

**Overall Assessment:** Highly inconsistent chunking strategies across parsers 