# PDF Parser & Vector Store Pipeline - Comprehensive Documentation

A powerful, extensible pipeline for parsing PDFs, extracting structured content (including tables), chunking text and tables, and storing the results in a variety of vector databases for downstream applications such as semantic search, retrieval-augmented generation, and document analysis.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Folder-by-Folder Guide](#folder-by-folder-guide)
6. [Core Components](#core-components)
7. [Analyzer Switching Guide](#analyzer-switching-guide)
8. [OpenAI VLM Integration](#openai-vlm-integration)
9. [Chunking System](#chunking-system)
10. [Chunk Size Consistency Fix](#chunk-size-consistency-fix)
11. [Vector Store Configuration](#vector-store-configuration)
12. [Parser System](#parser-system)
13. [Docker Setup](#docker-setup)
14. [Environment Management](#environment-management)
15. [Troubleshooting](#troubleshooting)
16. [References & Credits](#references--credits)

---

## Project Overview

This project provides a robust, extensible pipeline for parsing PDFs, extracting structured content (including tables), chunking text and tables, and storing the results in a variety of vector databases for downstream applications such as semantic search, retrieval-augmented generation, and document analysis.

---

## Features

- **Multi-parser support:** Handles native, scanned, math-heavy, and complex PDFs using specialized parsers
- **Advanced table and text extraction:** Preserves structure and formatting
- **Flexible chunking:** Recursive, hybrid, and tokenizer-based strategies
- **Vector database integration:** Supports FAISS, Milvus, Chroma, Pinecone, Qdrant, Weaviate
- **Environment management:** Seamless switching between parser and vector DB dependencies
- **Streamlit UI:** Interactive web interface for uploading, parsing, and exploring PDFs
- **Dockerized vector DBs:** Easy local or cloud deployment
- **Multiple analyzers:** OpenAI VLM, Ollama, and CLIP for PDF classification

---

## Installation

### System Requirements

- **Operating System**: macOS, Linux, or Windows (WSL2 recommended for Windows)
- **Python**: 3.10 or higher
- **Conda**: Miniconda or Anaconda
- **Docker**: For vector database services (optional)
- **Git**: For cloning the repository
- **Memory**: At least 8GB RAM (16GB recommended)
- **Storage**: At least 10GB free space

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/santhosh5113/pdf_parser_accelerator.git
cd pdf_parser_accelerator

# 2. Create the main pipeline environment
conda env create -f envs/pipeline_env.yml

# 3. Activate the environment
conda activate pipeline_env

# 4. Install vector store environments (optional)
conda env create -f database/chroma_env/environment.yml
conda env create -f database/faiss_env/environment.yml
conda env create -f database/qdrant_env/environment.yml
conda env create -f database/weaviate_env/environment.yml
conda env create -f database/milvus_env/milvus_env.yml

# 5. Install parser environments (optional)
conda env create -f parsers/docling_env/environment.yml
conda env create -f parsers/landingai_env/environment.yml
conda env create -f parsers/pdfplumber_env/environment.yml
conda env create -f parsers/mupdf_env/environment.yml
```

---

## Usage

### Basic Usage

```bash
# Process a single PDF
python -m database.run_pipeline input.pdf output.json --vector-store chroma

# Use specific analyzer
python -m database.run_pipeline input.pdf output.json --vector-store chroma --analyzer openai_vlm

# Start Streamlit web interface
streamlit run streamlit_app.py
```

### Web Interface

1. Start the Streamlit app: `streamlit run streamlit_app.py`
2. Open browser to `http://localhost:8501`
3. Upload your PDF file
4. Select vector store and analyzer
5. Click "Parse" and wait for processing
6. Download results or explore vector database

---

## Folder-by-Folder Guide

### 📁 `analyzer/` - PDF Analysis Components

**Purpose**: Contains different PDF analyzers for classifying and understanding PDF content.

**Files**:
- `analyze_pdf.py` - Basic PDF analyzer 
- `analyze_pdf2.py` - Ollama-based analyzer with LLaVA models
- `analyze_pdf3.py` - Enhanced CLIP analyzer with better prompts
- `analyze_pdf4.py` - OpenAI VLM analyzer using GPT-4 Vision

**Usage**:
```python
# Import analyzers
from analyzer.analyze_pdf import analyze_pdf_with_clip
from analyzer.analyze_pdf2 import analyze_image_with_ollama
from analyzer.analyze_pdf4 import analyze_pdf_with_openai_vlm

# Use CLIP analyzer (local, no API key needed)
result = analyze_pdf_with_clip("document.pdf")

# Use Ollama analyzer (local, requires Ollama)
result = analyze_image_with_ollama("image.png", "Describe this image", "llava:13b")

# Use OpenAI VLM (requires API key)
result = analyze_pdf_with_openai_vlm("document.pdf", "What type of document is this?")
```

**Configuration**:
- Set `OPENAI_API_KEY` environment variable for OpenAI VLM
- Install Ollama and pull models: `ollama pull llava:13b`
- No configuration needed for CLIP analyzer

### 📁 `config/` - Configuration Files

**Purpose**: Centralized configuration for vector stores and project settings.

**Files**:
- `vector_store_config.py` - Vector store configurations and settings
- `__init__.py` - Package initialization

**Key Configurations**:
```python
# Vector Store Selection
VECTOR_STORE_CONFIG = CHROMA_CONFIG  # Use ChromaDB
# VECTOR_STORE_CONFIG = QDRANT_CONFIG  # Use Qdrant
# VECTOR_STORE_CONFIG = WEAVIATE_CONFIG  # Use Weaviate
# VECTOR_STORE_CONFIG = MILVUS_CONFIG  # Use Milvus
# VECTOR_STORE_CONFIG = FAISS_CONFIG  # Use FAISS

# Chunking Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 100
```

**Environment Variables**:
```bash
# Required for cloud services
export OPENAI_API_KEY='your-openai-api-key'
export QDRANT_API_KEY='your-qdrant-api-key'
export WEAVIATE_API_KEY='your-weaviate-api-key'
export MILVUS_API_KEY='your-milvus-api-key'
```

### 📁 `database/` - Core Pipeline and Vector Stores

**Purpose**: Contains the main pipeline logic, vector store implementations, and text chunking.

**Key Files**:
- `run_pipeline.py` - Main pipeline orchestrator
- `text_chunker.py` - Advanced text chunking with table handling
- `vector_store_*.py` - Vector store implementations
- `bge_embedder.py` - BGE embedding model integration

**Vector Store Implementations**:
- `vector_store_chroma.py` - ChromaDB implementation
- `vector_store_faiss.py` - FAISS implementation
- `vector_store_qdrant.py` - Qdrant implementation
- `vector_store_weaviate.py` - Weaviate implementation
- `vector_store_milvus.py` - Milvus implementation

**Environment Folders**:
- `chroma_env/` - ChromaDB environment
- `faiss_env/` - FAISS environment
- `qdrant_env/` - Qdrant environment
- `weaviate_env/` - Weaviate environment
- `milvus_env/` - Milvus environment

**Usage**:
```python
# Run the main pipeline
python -m database.run_pipeline input.pdf output.json --vector-store chroma

# Use specific chunking strategy
python -m database.run_pipeline input.pdf output.json --chunk-strategy hybrid

# Process with custom parameters
python -m database.run_pipeline input.pdf output.json --chunk-size 500 --chunk-overlap 100
```

**Pipeline Flow**:
1. **PDF Analysis**: Analyzer determines PDF type
2. **Parser Selection**: Routes to appropriate parser
3. **Content Extraction**: Extracts text and tables
4. **Chunking**: Splits content into manageable chunks
5. **Embedding**: Generates embeddings for chunks
6. **Storage**: Stores in selected vector database

### 📁 `docker/` - Vector Database Services

**Purpose**: Docker configurations for running vector databases locally.

**Services**:
- `qdrant/` - Qdrant vector database
- `weaviate/` - Weaviate vector database
- `milvus/` - Milvus vector database

**Setup Instructions**:
```bash
# Start Qdrant
cd docker/qdrant
docker-compose up -d

# Start Weaviate
cd docker/weaviate
docker-compose up -d

# Start Milvus
cd docker/milvus
docker-compose up -d
```

**Configuration**:
- **Qdrant**: Runs on `localhost:6333`
- **Weaviate**: Runs on `localhost:8080`
- **Milvus**: Runs on `localhost:19530`

**Data Persistence**:
- Data is stored in `docker/*/volumes/` directories
- These directories are excluded from Git via `.gitignore`
- Data persists between container restarts

### 📁 `envs/` - Conda Environment Files

**Purpose**: Contains the main pipeline environment configuration.

**Files**:
- `pipeline_env.yml` - Main pipeline environment with all dependencies

**Dependencies Included**:
- Core Python packages (numpy, torch, streamlit)
- PDF processing libraries (pymupdf, pdfplumber)
- Vector store clients (chromadb, qdrant-client, weaviate-client)
- API libraries (fastapi, uvicorn, requests)
- Development tools (pytest, black, isort, flake8)

**Installation**:
```bash
# Create the main environment
conda env create -f envs/pipeline_env.yml

# Activate the environment
conda activate pipeline_env
```

### 📁 `parsers/` - PDF Parsing Components

**Purpose**: Contains all PDF parsers and their environment configurations.

**Parser Categories**:

**1. Table-Focused Parsers**:
- `docling_parser.py` - Specialized for table extraction
- `camelot_parser.py` - Advanced table detection
- `paddleocr_parser.py` - OCR-based table extraction

**2. Text-Focused Parsers**:
- `mupdf_parser.py` - Native PDF text extraction
- `pdfplumber_parser.py` - Simple text extraction
- `pdfminer_parser.py` - Low-level text extraction

**3. Vision-Based Parsers**:
- `landingai_parser.py` - Vision AI for complex documents
- `vision_parser.py` - General vision-based parsing
- `donut_parser.py` - Document understanding transformer

**4. Specialized Parsers**:
- `llama_parser.py` - LlamaParse for complex documents
- `nougat_parser.py` - Nougat for academic papers
- `layoutlmv3_parser.py` - Layout-aware parsing
- `llmwhisperer_parser.py` - LLMWhisperer API integration

**Environment Folders**:
Each parser has its own environment folder:
- `docling_env/` - Docling parser environment
- `landingai_env/` - LandingAI parser environment
- `pdfplumber_env/` - PDFPlumber environment
- `mupdf_env/` - PyMuPDF environment
- `camelot_env/` - Camelot environment
- `donut_env/` - Donut environment
- `layoutlm_env/` - LayoutLM environment
- `llama_parse_env/` - LlamaParse environment
- `llmwhisperer_env/` - LLMWhisperer environment
- `markitdown_env/` - Markitdown environment
- `nougat_env/` - Nougat environment
- `paddleocr_env/` - PaddleOCR environment
- `pdfminer_env/` - PDFMiner environment
- `vision_env/` - Vision parser environment

**Installation**:
```bash
# Install parser environments as needed
conda env create -f parsers/docling_env/environment.yml
conda env create -f parsers/landingai_env/environment.yml
conda env create -f parsers/pdfplumber_env/environment.yml
conda env create -f parsers/mupdf_env/environment.yml
```

**Usage**:
```python
# Import parsers
from parsers.docling_parser import parse_pdf_with_docling
from parsers.mupdf_parser import parse_pdf_with_mupdf
from parsers.landingai_parser import parse_pdf_with_landingai

# Use Docling for tables
result = parse_pdf_with_docling("document.pdf")

# Use PyMuPDF for text
result = parse_pdf_with_mupdf("document.pdf")

# Use LandingAI for complex documents
result = parse_pdf_with_landingai("document.pdf")
```

**Parser Selection Logic**:
The pipeline automatically selects the best parser based on:
1. **PDF Type**: Native vs scanned
2. **Content Type**: Text-heavy vs table-heavy vs image-heavy
3. **Complexity**: Simple vs complex layout
4. **Special Requirements**: Math, equations, diagrams

### 📁 `shared/` - Input/Output Folders

**Purpose**: Centralized location for input PDFs and output results.

**Structure**:
```
shared/
├── input_pdfs/     # Upload your PDFs here
│   ├── .gitkeep   # Ensures folder is tracked by Git
│   └── README.md   # Usage instructions
└── output_json/    # Processed results
    ├── .gitkeep   # Ensures folder is tracked by Git
    └── README.md   # Usage instructions
```

**Usage**:
```bash
# Place your PDFs in the input folder
cp your_document.pdf shared/input_pdfs/

# Process the PDF
python -m database.run_pipeline shared/input_pdfs/your_document.pdf shared/output_json/result.json

# Results will be saved in output_json/
```

**File Organization**:
- **Input**: All PDF files go in `shared/input_pdfs/`
- **Output**: All JSON results go in `shared/output_json/`
- **Temporary**: Processing artifacts are cleaned up automatically
- **Git Tracking**: Only folder structure is tracked, not actual files

### 📁 `nougat/` - Nougat Parser Integration

**Purpose**: Contains the Nougat parser implementation for academic papers.

**Files**:
- `predict.py` - Main prediction script
- `train.py` - Training script
- `app.py` - Web application
- `lightning_module.py` - PyTorch Lightning module
- Configuration files and documentation

**Usage**:
```python
# Import Nougat parser
from parsers.nougat_parser import parse_pdf_with_nougat

# Parse academic papers
result = parse_pdf_with_nougat("academic_paper.pdf")
```

**Installation**:
```bash
# Install Nougat environment
conda env create -f parsers/nougat_env/environment.yml

# Activate environment
conda activate nougat_env
```

### 📁 Utility Files

**`streamlit_app.py`** - Web Interface
- Interactive Streamlit application
- PDF upload and processing
- Vector database exploration
- Results visualization

**`view_all_vector_db_chunks.py`** - Database Viewer
- View all stored chunks in vector databases
- Search and filter functionality
- Export capabilities

**`clear_all_vector_dbs.py`** - Database Cleaner
- Clear all vector database data
- Reset to clean state
- Useful for testing and development

---

## Core Components

### Pipeline Architecture

The pipeline follows this flow:

1. **Input**: PDF file uploaded or specified
2. **Analysis**: PDF type determined by analyzer
3. **Parsing**: Content extracted by appropriate parser
4. **Chunking**: Text and tables split into chunks
5. **Embedding**: Chunks converted to vector embeddings
6. **Storage**: Embeddings stored in vector database
7. **Output**: Results saved as JSON and available for search

### Analyzer System

**Available Analyzers**:
- **OpenAI VLM**: Uses GPT-4 Vision for PDF analysis
- **Ollama**: Local analysis using LLaVA models
- **CLIP**: Local analysis using CLIP model

**Selection Criteria**:
- **OpenAI VLM**: Best accuracy, requires API key
- **Ollama**: Good balance, local processing
- **CLIP**: Fastest, local processing

### Parser System

**Parser Categories**:
1. **Table-Focused**: Docling, Camelot, PaddleOCR
2. **Text-Focused**: PyMuPDF, PDFPlumber, PDFMiner
3. **Vision-Based**: LandingAI, Vision Parser, Donut
4. **Specialized**: LlamaParse, Nougat, LayoutLM

**Selection Logic**:
- **Tables Present**: Use Docling or Camelot
- **Complex Layout**: Use LandingAI or Vision Parser
- **Academic Papers**: Use Nougat
- **Simple Text**: Use PyMuPDF or PDFPlumber
- **Scanned Documents**: Use PaddleOCR or Vision Parser

### Vector Store System

**Supported Databases**:
- **ChromaDB**: Local, simple, good for development
- **FAISS**: Local, fast, good for large datasets
- **Qdrant**: Cloud-ready, good for production
- **Weaviate**: Enterprise-ready, feature-rich
- **Milvus**: High-performance, scalable

**Selection Criteria**:
- **Development**: Use ChromaDB or FAISS
- **Production**: Use Qdrant or Weaviate
- **Large Scale**: Use Milvus
- **Cloud**: Use Qdrant Cloud or Weaviate Cloud

---

## Analyzer Switching Guide

### Quick Switching Method

Edit `database/run_pipeline.py` and modify the `DEFAULT_ANALYZER` variable:

```python
# ===== QUICK SWITCHING: Change default analyzer here =====
# Uncomment the analyzer you want to use as default:
DEFAULT_ANALYZER = "openai_vlm"  # OpenAI VLM (requires API key)
# DEFAULT_ANALYZER = "ollama"     # Ollama (local, no API key needed)
# DEFAULT_ANALYZER = "clip"       # CLIP (local, no API key needed)
```

### Command Line Override

```bash
# Use OpenAI VLM (default)
python -m database.run_pipeline input.pdf output.json

# Use Ollama
python -m database.run_pipeline input.pdf output.json --analyzer ollama

# Use CLIP
python -m database.run_pipeline input.pdf output.json --analyzer clip
```

### Analyzer Comparison

| Analyzer | Accuracy | Speed | API Key | Local | Best For |
|----------|----------|-------|---------|-------|----------|
| OpenAI VLM | High | Medium | Required | No | Production |
| Ollama | Medium | Fast | No | Yes | Development |
| CLIP | Low | Very Fast | No | Yes | Quick Testing |

---

## OpenAI VLM Integration

### Setup

1. **Get API Key**: Sign up at https://platform.openai.com/
2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
3. **Install Dependencies**: Already included in `pipeline_env.yml`

### Usage

```python
from analyzer.analyze_pdf4 import analyze_pdf_with_openai_vlm

# Analyze PDF type
result = analyze_pdf_with_openai_vlm("document.pdf", "What type of document is this?")

# Extract specific information
result = analyze_pdf_with_openai_vlm("document.pdf", "Extract all tables from this document")

# Complex analysis
result = analyze_pdf_with_openai_vlm("document.pdf", "Analyze the structure and content of this document")
```

### Cost Optimization

- Use specific prompts to reduce token usage
- Process smaller PDFs when possible
- Cache results for repeated analysis
- Use local analyzers for development/testing

---

## Chunking System

### Overview

The chunking system in `database/text_chunker.py` provides multiple strategies for splitting PDF content into manageable chunks for vector storage.

### Strategies

**1. Hybrid Chunking (Recommended)**
- Keeps tables as single chunks
- Splits text recursively by size
- Preserves table structure
- Best for mixed content

**2. Recursive Chunking**
- Splits all content recursively
- Uses character count and overlap
- Good for text-heavy documents
- Configurable chunk size and overlap

**3. Tokenizer-Based Chunking**
- Uses token count instead of characters
- More accurate for LLM applications
- Slower but more precise
- Good for specific token limits

### Configuration

```python
# Chunking parameters
CHUNK_SIZE = 1000        # Characters per chunk
CHUNK_OVERLAP = 200      # Overlap between chunks
MIN_CHUNK_CHARS = 100    # Minimum chunk size
CHUNK_STRATEGY = "hybrid"  # Strategy to use
```

### Table Handling

**Special Features**:
- Tables are kept as single chunks
- Multiple table formats supported (markdown, HTML, CSV, grid)
- Table metadata preserved
- Automatic table detection

**Table Formats**:
```python
# Markdown format
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

# HTML format
<table><tr><td>Data</td></tr></table>

# CSV format
Column 1,Column 2
Data 1,Data 2

# Grid format
┌─────────┬─────────┐
│ Column 1│ Column 2│
├─────────┼─────────┤
│ Data 1  │ Data 2  │
└─────────┴─────────┘
```

---

## Chunk Size Consistency Fix

### Problem

Different parsers were producing inconsistent chunk sizes due to:
- Different text extraction methods
- Inconsistent table handling
- Varying whitespace processing
- Different metadata inclusion

### Solution

**1. Standardized Text Processing**
- Normalize whitespace across all parsers
- Consistent text cleaning procedures
- Unified metadata handling

**2. Table-Aware Chunking**
- Tables always kept as single chunks
- Consistent table format conversion
- Preserved table structure and metadata

**3. Configurable Parameters**
- Centralized chunk size configuration
- Consistent overlap handling
- Minimum chunk size enforcement

### Implementation

```python
# In text_chunker.py
def chunk_content(content, chunk_size=1000, chunk_overlap=200, strategy="hybrid"):
    """
    Standardized chunking function for all parsers
    """
    if strategy == "hybrid":
        return hybrid_chunk_content(content, chunk_size, chunk_overlap)
    elif strategy == "recursive":
        return recursive_chunk_content(content, chunk_size, chunk_overlap)
    elif strategy == "tokenizer":
        return tokenizer_chunk_content(content, chunk_size, chunk_overlap)
```

### Benefits

- **Consistency**: All parsers produce similar chunk sizes
- **Quality**: Better chunk quality and relevance
- **Flexibility**: Easy to switch between strategies
- **Maintainability**: Centralized chunking logic

---

## Vector Store Configuration

### Configuration File

Edit `config/vector_store_config.py` to switch between vector stores:

```python
# Vector store configurations
CHROMA_CONFIG = {
    "type": "chroma",
    "host": "localhost",
    "port": 8000,
    "collection_name": "pdf_chunks"
}

QDRANT_CONFIG = {
    "type": "qdrant",
    "host": "localhost",
    "port": 6333,
    "collection_name": "pdf_chunks"
}

WEAVIATE_CONFIG = {
    "type": "weaviate",
    "host": "localhost",
    "port": 8080,
    "class_name": "PdfChunk"
}

# Active configuration (uncomment one)
VECTOR_STORE_CONFIG = CHROMA_CONFIG  # Use ChromaDB
# VECTOR_STORE_CONFIG = QDRANT_CONFIG  # Use Qdrant
# VECTOR_STORE_CONFIG = WEAVIATE_CONFIG  # Use Weaviate
```

### Environment Variables

```bash
# For cloud services
export QDRANT_API_KEY='your-qdrant-api-key'
export WEAVIATE_API_KEY='your-weaviate-api-key'
export MILVUS_API_KEY='your-milvus-api-key'

# For local services (optional)
export CHROMA_HOST='localhost'
export QDRANT_HOST='localhost'
export WEAVIATE_HOST='localhost'
```

### Database Setup

**ChromaDB (Local)**:
```bash
# No setup needed - runs in memory or local files
python -m database.run_pipeline input.pdf output.json --vector-store chroma
```

**Qdrant (Local)**:
```bash
# Start Qdrant service
cd docker/qdrant
docker-compose up -d

# Use Qdrant
python -m database.run_pipeline input.pdf output.json --vector-store qdrant
```

**Weaviate (Local)**:
```bash
# Start Weaviate service
cd docker/weaviate
docker-compose up -d

# Use Weaviate
python -m database.run_pipeline input.pdf output.json --vector-store weaviate
```

**FAISS (Local)**:
```bash
# No setup needed - runs locally
python -m database.run_pipeline input.pdf output.json --vector-store faiss
```

**Milvus (Local)**:
```bash
# Start Milvus service
cd docker/milvus
docker-compose up -d

# Use Milvus
python -m database.run_pipeline input.pdf output.json --vector-store milvus
```

---

## Parser System

### Parser Selection

The pipeline automatically selects the best parser based on:

1. **PDF Analysis**: Analyzer determines PDF characteristics
2. **Content Type**: Text-heavy vs table-heavy vs image-heavy
3. **Complexity**: Simple vs complex layout
4. **Special Requirements**: Math, equations, diagrams

### Parser Categories

**Table-Focused Parsers**:
- **Docling**: Best for structured tables
- **Camelot**: Advanced table detection
- **PaddleOCR**: OCR-based table extraction

**Text-Focused Parsers**:
- **PyMuPDF**: Native PDF text extraction
- **PDFPlumber**: Simple text extraction
- **PDFMiner**: Low-level text extraction

**Vision-Based Parsers**:
- **LandingAI**: Vision AI for complex documents
- **Vision Parser**: General vision-based parsing
- **Donut**: Document understanding transformer

**Specialized Parsers**:
- **LlamaParse**: Complex document parsing
- **Nougat**: Academic paper parsing
- **LayoutLM**: Layout-aware parsing
- **LLMWhisperer**: API-based parsing

### Parser Installation

```bash
# Install parser environments as needed
conda env create -f parsers/docling_env/environment.yml
conda env create -f parsers/landingai_env/environment.yml
conda env create -f parsers/pdfplumber_env/environment.yml
conda env create -f parsers/mupdf_env/environment.yml
conda env create -f parsers/camelot_env/environment.yml
conda env create -f parsers/donut_env/environment.yml
conda env create -f parsers/layoutlm_env/environment.yml
conda env create -f parsers/llama_parse_env/environment.yml
conda env create -f parsers/llmwhisperer_env/environment.yml
conda env create -f parsers/markitdown_env/environment.yml
conda env create -f parsers/nougat_env/environment.yml
conda env create -f parsers/paddleocr_env/environment.yml
conda env create -f parsers/pdfminer_env/environment.yml
conda env create -f parsers/vision_env/environment.yml
```

### Parser Usage

```python
# Import parsers
from parsers.docling_parser import parse_pdf_with_docling
from parsers.mupdf_parser import parse_pdf_with_mupdf
from parsers.landingai_parser import parse_pdf_with_landingai
from parsers.camelot_parser import parse_pdf_with_camelot
from parsers.nougat_parser import parse_pdf_with_nougat

# Use specific parsers
result = parse_pdf_with_docling("document.pdf")
result = parse_pdf_with_mupdf("document.pdf")
result = parse_pdf_with_landingai("document.pdf")
result = parse_pdf_with_camelot("document.pdf")
result = parse_pdf_with_nougat("academic_paper.pdf")
```

### Parser Output Formats

**Docling Format**:
```json
{
  "tables": [{"content": "table_data", "format": "markdown"}],
  "texts": [{"content": "text_content", "page": 1}]
}
```

**PyMuPDF Format**:
```json
{
  "items": [
    {"type": "text", "content": "text_content", "page": 1},
    {"type": "table", "content": "table_data", "page": 1}
  ]
}
```

**LandingAI Format**:
```json
{
  "items": [
    {"chunk_type": "text", "content": "text_content", "page": 1},
    {"chunk_type": "table", "content": "table_data", "page": 1}
  ]
}
```

---

## Docker Setup

### Vector Database Services

**Qdrant Setup**:
```bash
# Navigate to Qdrant directory
cd docker/qdrant

# Start Qdrant service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs

# Stop service
docker-compose down
```

**Weaviate Setup**:
```bash
# Navigate to Weaviate directory
cd docker/weaviate

# Start Weaviate service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs

# Stop service
docker-compose down
```

**Milvus Setup**:
```bash
# Navigate to Milvus directory
cd docker/milvus

# Start Milvus service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs

# Stop service
docker-compose down
```

### Service URLs

- **Qdrant**: http://localhost:6333
- **Weaviate**: http://localhost:8080
- **Milvus**: http://localhost:19530

### Data Persistence

Data is stored in Docker volumes:
- `docker/qdrant/qdrant_storage/`
- `docker/weaviate/data/`
- `docker/milvus/volumes/`

These directories are excluded from Git via `.gitignore`.

### Troubleshooting Docker

**Common Issues**:
1. **Port conflicts**: Change ports in `docker-compose.yml`
2. **Memory issues**: Increase Docker memory allocation
3. **Permission issues**: Check file permissions in volume directories

**Debug Commands**:
```bash
# Check Docker status
docker ps

# View container logs
docker logs <container_name>

# Access container shell
docker exec -it <container_name> /bin/bash

# Restart services
docker-compose restart
```

---

## Environment Management

### Conda Environment Structure

**Main Environment**: `pipeline_env`
- Contains core dependencies
- Used for main pipeline execution
- Includes all vector store clients

**Vector Store Environments**:
- `chroma_env`: ChromaDB dependencies
- `faiss_env`: FAISS dependencies
- `qdrant_env`: Qdrant dependencies
- `weaviate_env`: Weaviate dependencies
- `milvus_env`: Milvus dependencies

**Parser Environments**:
- `docling_env`: Docling parser dependencies
- `landingai_env`: LandingAI parser dependencies
- `pdfplumber_env`: PDFPlumber dependencies
- `mupdf_env`: PyMuPDF dependencies
- And many more for each parser

### Environment Activation

```bash
# Activate main environment
conda activate pipeline_env

# Activate specific environments as needed
conda activate chroma_env
conda activate docling_env
conda activate landingai_env
```

### Environment Switching

The pipeline automatically switches environments:
1. **Main Pipeline**: Uses `pipeline_env`
2. **Parser Execution**: Switches to parser-specific environment
3. **Vector Store**: Uses vector store-specific environment
4. **Return to Main**: Returns to `pipeline_env`

### Environment Troubleshooting

**Recreate Environment**:
```bash
# Remove and recreate environment
conda env remove -n pipeline_env
conda env create -f envs/pipeline_env.yml
```

**Update Environment**:
```bash
# Update existing environment
conda env update -f envs/pipeline_env.yml
```

**Check Environment**:
```bash
# List all environments
conda env list

# Check current environment
conda info --envs

# List packages in environment
conda list
```

---

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Make sure you're in the correct environment
conda activate pipeline_env

# Reinstall the environment if needed
conda env remove -n pipeline_env
conda env create -f envs/pipeline_env.yml
```

**2. "API key not set" errors**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'

# Set other API keys as needed
export QDRANT_API_KEY='your-qdrant-api-key'
export WEAVIATE_API_KEY='your-weaviate-api-key'
```

**3. Docker services not starting**
```bash
# Check if Docker is running
docker --version

# Start Docker services
cd docker/qdrant
docker-compose up -d

# Check service status
docker-compose ps
```

**4. Memory issues**
- Close other applications
- Use FAISS or ChromaDB instead of Milvus
- Process smaller PDFs
- Increase system memory

**5. Parser errors**
```bash
# Check parser environment
conda activate docling_env  # or relevant parser env

# Reinstall parser environment
conda env remove -n docling_env
conda env create -f parsers/docling_env/environment.yml
```

**6. Vector store connection errors**
```bash
# Check if services are running
curl http://localhost:6333  # Qdrant
curl http://localhost:8080  # Weaviate
curl http://localhost:19530 # Milvus

# Restart Docker services
cd docker/qdrant
docker-compose restart
```

### Performance Optimization

**1. Use Local Vector Stores**
- ChromaDB and FAISS run locally
- No network latency
- Faster processing

**2. Optimize Chunk Size**
- Smaller chunks for better search
- Larger chunks for faster processing
- Balance based on your use case

**3. Use Appropriate Parsers**
- Simple text: Use PyMuPDF or PDFPlumber
- Tables: Use Docling or Camelot
- Complex documents: Use LandingAI or Vision Parser

**4. Batch Processing**
```bash
# Process multiple PDFs efficiently
for pdf in documents/*.pdf; do
    python -m database.run_pipeline "$pdf" "output/$(basename "$pdf" .pdf).json" --vector-store chroma
done
```

### Getting Help

1. **Check Logs**: Look at terminal output for error messages
2. **Verify Environments**: Ensure all environments are created correctly
3. **Check API Keys**: Verify environment variables are set
4. **Test Services**: Ensure Docker services are running
5. **Read Documentation**: Check this comprehensive guide

---

## References & Credits

### Libraries and Frameworks

- **PDF Processing**: PyMuPDF, PDFPlumber, PDFMiner, Camelot
- **Vision AI**: LandingAI, Donut, LayoutLM, CLIP
- **Vector Databases**: ChromaDB, FAISS, Qdrant, Weaviate, Milvus
- **Machine Learning**: PyTorch, Transformers, Sentence Transformers
- **Web Framework**: Streamlit, FastAPI
- **Containerization**: Docker, Docker Compose

### Models and APIs

- **OpenAI**: GPT-4 Vision API
- **Hugging Face**: BGE embeddings, CLIP model
- **Ollama**: LLaVA models
- **LandingAI**: Vision API
- **Llama Cloud**: LlamaParse API

### Community and Resources

- **Vector Database Communities**: ChromaDB, Qdrant, Weaviate, Milvus
- **PDF Processing**: PyMuPDF, PDFPlumber communities
- **Machine Learning**: Hugging Face, PyTorch communities
- **Open Source**: GitHub communities and contributors

### Acknowledgments

- **OpenAI** for GPT-4 Vision API
- **Hugging Face** for transformer models and libraries
- **Vector database communities** for excellent documentation and support
- **PDF parsing libraries** for robust text and table extraction
- **Open source contributors** for continuous improvements

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*This comprehensive documentation covers all aspects of the PDF Parser & Vector Store Pipeline. For additional support, please refer to the individual component documentation or create an issue in the repository.* 
