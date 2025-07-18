Read file: README.md
Here is a full, professional draft README for your project, incorporating all the details and structure we discussed. You can copy this into your `README.md` and adjust as needed.

---

# PDF Parser & Vector Store Pipeline

A powerful, extensible pipeline for parsing PDFs, extracting structured content (including tables), chunking text and tables, and storing the results in a variety of vector databases for downstream applications such as semantic search, retrieval-augmented generation, and document analysis.

---

## Features

- **Multi-parser support:** Handles native, scanned, math-heavy, and complex PDFs using specialized parsers.
- **Advanced table and text extraction:** Preserves structure and formatting.
- **Flexible chunking:** Recursive, hybrid, and tokenizer-based strategies.
- **Vector database integration:** Supports FAISS, Milvus, Chroma, Pinecone, Qdrant, Weaviate.
- **Environment management:** Seamless switching between parser and vector DB dependencies.
- **Streamlit UI:** Interactive web interface for uploading, parsing, and exploring PDFs.
- **Dockerized vector DBs:** Easy local or cloud deployment.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Core Components](#core-components)
   - [Parsers](#parsers-parsers)
   - [Chunking](#chunking-databasetext_chunkerpy)
   - [Vector Store Integration](#vector-store-integration-database)
   - [Pipeline](#pipeline-databaserun_pipelinepy)
   - [Configuration](#configuration-config)
   - [Analyzer](#analyzer-analyzer)
   - [Streamlit App](#streamlit-app-streamlit_apppy)
4. [Docker & Environment Management](#docker--environment-management)
5. [Data & Shared Resources](#data--shared-resources)
6. [Extending the Project](#extending-the-project)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting & FAQ](#troubleshooting--faq)
9. [References & Credits](#references--credits)

---

## Project Overview

This project provides a robust, extensible pipeline for parsing PDFs, extracting structured content (including tables), chunking text and tables, and storing the results in a variety of vector databases for downstream applications such as semantic search, retrieval-augmented generation, and document analysis.

---

## Directory Structure

```
pdf_parser_project/
│
├── analyzer/                # PDF type/category detection logic
├── chroma_db/               # Chroma vector DB data (if used)
├── config/                  # Configuration files for chunking, vector stores, etc.
├── database/                # Chunking, vector store integration, pipeline logic
├── docker/                  # Docker configs for vector DBs
├── faiss_index/             # FAISS index data (if used)
├── LLaVA/                   # LLaVA model and related scripts/docs
├── nougat/                  # (Reserved for Nougat parser/model)
├── parsers/                 # All PDF parsers (Docling, Llama, LandingAI, etc.)
├── prompt_images/           # Images used for prompt examples
├── shared/                  # Input PDFs, output JSONs, and shared resources
├── small_dataset/           # Sample PDFs for testing
├── streamlit_app.py         # Streamlit UI for the pipeline
├── switch_vector_store.sh   # Script to switch vector DB environments
├── view_all_vector_db_chunks.py # Utility to view stored chunks
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation (this file)
```

---

## Core Components

### Parsers (`parsers/`)

- **Purpose:**  
  Each parser is designed to handle a specific type of PDF or extraction task.
  - `llama_parser.py`: Uses LlamaParse for scanned or complex PDFs.
  - `docling_parser.py`: Uses Docling for native tables and structured content.
  - `landingai_parser.py`: Uses LandingAI for math-heavy or visually complex PDFs.
  - Many other parsers for OCR, layout, and specialized extraction.

- **Adding a New Parser:**  
  1. Create a new parser script in `parsers/`.
  2. Ensure it outputs JSON in a documented structure.
  3. Register it in the pipeline logic (`run_pipeline.py`).

- **Supported Output Structures:**  
  - `items` array (Llama, Markitdown, etc.)
  - `tables` and `texts` arrays (Docling)
  - `chunk_type` and `captions` (LandingAI)
  - See each parser’s docstring for details.

---

### Chunking (`database/text_chunker.py`)

- **Purpose:**  
  Splits extracted text and tables into manageable chunks for embedding and storage.

- **How it Handles Different Parsers:**  
  - Detects parser output format and extracts tables as single chunks, text as recursively split chunks.
  - Supports markdown, HTML, CSV, and grid formats for tables.

- **Chunking Strategies:**  
  - **Hybrid:** Keeps tables as single chunks, splits text recursively.
  - **Recursive:** Splits all content recursively by size/overlap.
  - **Tokenizer-based:** Uses token count for chunking.

---

### Vector Store Integration (`database/`)

- **Supported Vector DBs:**  
  - FAISS, Milvus, Chroma, Pinecone, Qdrant, Weaviate

- **Switching:**  
  - Use `switch_vector_store.sh` or pipeline arguments to select backend.

- **Storage:**  
  - Chunks are stored with metadata (source, chunk type, index, etc.)
  - Embeddings generated via BGE or other models.

---

### Pipeline (`database/run_pipeline.py`)

- **End-to-End Flow:**  
  1. Detect PDF type (analyzer).
  2. Route to appropriate parser.
  3. Parse and extract content.
  4. Chunk content.
  5. Store in selected vector DB.

- **Environment Management:**  
  - Uses conda environments for parser/vector DB dependencies.
  - Switches environments as needed for each step.

---

### Configuration (`config/`)

- **Chunking and Vector Store Config:**  
  - `vector_store_config.py`: Vector DB settings.
  - `config.py`: General settings.

- **How to Change:**  
  - Edit config files or pass arguments to pipeline.

---

### Analyzer (`analyzer/`)

- **Purpose:**  
  Detects PDF type (native, scanned, table, math-heavy, etc.) to select the best parser.

---

### Streamlit App (`streamlit_app.py`)

- **Purpose:**  
  Provides a web UI for uploading PDFs, running the pipeline, and exploring results.

- **Features:**  
  - Upload and parse PDFs
  - View extracted tables and text
  - Search and visualize vector DB contents

---

## Docker & Environment Management

- **Docker:**  
  - Each vector DB has a Docker Compose setup in `docker/`.
  - Run with `docker-compose up` in the respective directory.

- **Conda Environments:**  
  - Each parser and vector DB may require a separate conda environment.
  - Use `switch_vector_store.sh` to activate the correct environment.

---

## Data & Shared Resources

- **Input PDFs:**  
  - Place in `shared/input_pdfs/`
- **Output JSONs:**  
  - Written to `shared/output_json/`
- **Sample Data:**  
  - `small_dataset/` contains example PDFs for testing.

---

## Extending the Project

- **Add a Parser:**  
  - See section on Parsers above.
- **Add a Vector Store:**  
  - Implement a new class in `database/` following the `VectorStoreBase` interface.
- **Add a Chunking Strategy:**  
  - Extend `text_chunker.py` with a new chunking function.

---

## Testing & Validation

- **Test Scripts:**  
  - `test_recrussive_split.py` for chunking
  - Manual and automated tests for parsing and storage

---

## Troubleshooting & FAQ

- **Common Issues:**  
  - Environment not activated: Use the correct conda env.
  - Parser errors: Check parser logs and dependencies.
  - Vector DB connection: Ensure Docker containers are running.

---

## References & Credits

- **Libraries:**  
  - LangChain, HuggingFace Transformers, FAISS, Milvus, Chroma, Pinecone, Qdrant, Weaviate, Streamlit, etc.
- **Models:**  
  - BGE, LLaVA, Docling, LlamaParse, LandingAI, etc.

---

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/pdf-parser-accelerator.git
cd pdf-parser-accelerator
pip install -r requirements.txt
```

---

## Usage

1. Place your PDFs in `shared/input_pdfs/`.
2. Run the pipeline via CLI or Streamlit app.
3. Explore results in the vector DB or via the UI.

