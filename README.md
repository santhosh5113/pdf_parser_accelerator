# PDF Parser & Vector Store Pipeline

A powerful, extensible pipeline for parsing PDFs, extracting structured content (including tables), chunking text and tables, and storing the results in a variety of vector databases for downstream applications such as semantic search, retrieval-augmented generation, and document analysis.

## 🚀 Quick Start

### System Requirements

- **Operating System**: macOS, Linux, or Windows (WSL2 recommended for Windows)
- **Python**: 3.10 or higher
- **Conda**: Miniconda or Anaconda
- **Docker**: For vector database services (optional)
- **Git**: For cloning the repository
- **Memory**: At least 8GB RAM (16GB recommended)
- **Storage**: At least 10GB free space

### Step 1: Clone the Repository

```bash
git clone https://github.com/santhosh5113/pdf_parser_accelerator.git
cd pdf_parser_accelerator
```

### Step 2: Install Conda (if not already installed)

**macOS/Linux:**
```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Or using Homebrew on macOS
brew install --cask miniconda
```

**Windows:**
```bash
# Download from https://docs.conda.io/en/latest/miniconda.html
# Or using Chocolatey
choco install miniconda3
```

### Step 3: Create and Activate the Main Environment

```bash
# Create the main pipeline environment
conda env create -f envs/pipeline_env.yml

# Activate the environment
conda activate pipeline_env
```

### Step 4: Install Vector Store Environments (Optional)

Choose which vector stores you want to use:

```bash
# For ChromaDB (recommended for beginners)
conda env create -f database/chroma_env/environment.yml

# For FAISS (lightweight, local)
conda env create -f database/faiss_env/environment.yml

# For Qdrant (cloud-ready)
conda env create -f database/qdrant_env/environment.yml

# For Weaviate (enterprise-ready)
conda env create -f database/weaviate_env/environment.yml

# For Milvus (high-performance)
conda env create -f database/milvus_env/milvus_env.yml
```

### Step 5: Install Parser Environments (Optional)

Install environments for the parsers you plan to use:

```bash
# For Docling parser (tables)
conda env create -f parsers/docling_env/environment.yml

# For LandingAI parser (math-heavy documents)
conda env create -f parsers/landingai_env/environment.yml

# For PDFPlumber parser (simple text extraction)
conda env create -f parsers/pdfplumber_env/environment.yml

# For PyMuPDF parser (native PDFs)
conda env create -f parsers/mupdf_env/environment.yml
```

### Step 6: Set Up API Keys (Optional)

For cloud-based services, set your API keys:

```bash
# OpenAI API (for VLM analyzer)
export OPENAI_API_KEY='your-openai-api-key-here'

# Qdrant Cloud (if using Qdrant)
export QDRANT_API_KEY='your-qdrant-api-key-here'

# Llama Cloud (for LlamaParse)
export LLAMA_CLOUD_API_KEY='your-llama-cloud-api-key-here'

# LLMWhisperer (for LLMWhisperer parser)
export LLMWHISPERER_API_KEY='your-llmwhisperer-api-key-here'
```

### Step 7: Start Vector Database Services (Optional)

**Option A: Using Docker (Recommended)**

```bash
# For Qdrant
cd docker/qdrant
docker-compose up -d

# For Weaviate
cd docker/weaviate
docker-compose up -d

# For Milvus
cd docker/milvus
docker-compose up -d
```

**Option B: Using Cloud Services**

- **Qdrant**: Use Qdrant Cloud (free tier available)
- **Weaviate**: Use Weaviate Cloud Services
- **ChromaDB**: Runs locally, no setup needed
- **FAISS**: Runs locally, no setup needed

### Step 8: Run the Application

**Method 1: Streamlit Web Interface (Recommended)**

```bash
# Make sure you're in the pipeline environment
conda activate pipeline_env

# Start the Streamlit app
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

**Method 2: Command Line Interface**

```bash
# Make sure you're in the pipeline environment
conda activate pipeline_env

# Process a single PDF
python -m database.run_pipeline path/to/your/document.pdf output.json --vector-store chroma
```

## 📁 Project Structure

```
pdf_parser_project/
├── analyzer/           # PDF analyzers (OpenAI VLM, Ollama, CLIP)
├── config/            # Vector store configurations
├── database/          # Vector store implementations and pipeline
├── docker/            # Docker configurations for vector stores
├── envs/              # Conda environment files
├── parsers/           # PDF parsers (Docling, LandingAI, etc.)
├── shared/            # Input/output folders
│   ├── input_pdfs/    # Upload your PDFs here
│   └── output_json/   # Processed results
├── streamlit_app.py   # Web interface
└── README.md          # This file
```

## 🔧 Configuration

### Vector Store Selection

Edit `config/vector_store_config.py` to switch between vector stores:

```python
# Uncomment the vector store you want to use:
VECTOR_STORE_CONFIG = CHROMA_CONFIG  # Use ChromaDB
# VECTOR_STORE_CONFIG = QDRANT_CONFIG  # Use Qdrant
# VECTOR_STORE_CONFIG = WEAVIATE_CONFIG  # Use Weaviate
# VECTOR_STORE_CONFIG = MILVUS_CONFIG  # Use Milvus
# VECTOR_STORE_CONFIG = FAISS_CONFIG  # Use FAISS
```

### Analyzer Selection

Edit `database/run_pipeline.py` to change the default analyzer:

```python
# Line 135: Change the default analyzer
DEFAULT_ANALYZER = "openai_vlm"  # OpenAI VLM (requires API key)
# DEFAULT_ANALYZER = "ollama"     # Ollama (local, no API key needed)
# DEFAULT_ANALYZER = "clip"       # CLIP (local, no API key needed)
```

## 🎯 Usage Examples

### Example 1: Process a PDF via Web Interface

1. Start the Streamlit app: `streamlit run streamlit_app.py`
2. Upload your PDF file
3. Select a vector store (ChromaDB recommended for beginners)
4. Click "Parse" and wait for processing
5. Download the results or explore the vector database

### Example 2: Process Multiple PDFs via Command Line

```bash
# Process a single PDF
python -m database.run_pipeline documents/report.pdf output.json --vector-store chroma

# Process with specific analyzer
python -m database.run_pipeline documents/report.pdf output.json --vector-store chroma --analyzer ollama

# Process with OpenAI VLM (requires API key)
python -m database.run_pipeline documents/report.pdf output.json --vector-store chroma --analyzer openai_vlm
```

### Example 3: Search Vector Database

```bash
# View all stored chunks
python view_all_vector_db_chunks.py

# Clear all vector databases
python clear_all_vector_dbs.py
```

## 🔍 Features

- **Multi-parser support**: Handles native, scanned, math-heavy, and complex PDFs
- **Advanced table and text extraction**: Preserves structure and formatting
- **Flexible chunking**: Recursive, hybrid, and tokenizer-based strategies
- **Vector database integration**: Supports FAISS, Milvus, Chroma, Pinecone, Qdrant, Weaviate
- **Environment management**: Seamless switching between parser and vector DB dependencies
- **Streamlit UI**: Interactive web interface for uploading, parsing, and exploring PDFs
- **Dockerized vector DBs**: Easy local or cloud deployment

## 🛠️ Troubleshooting

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
```

**3. Docker services not starting**
```bash
# Check if Docker is running
docker --version

# Start Docker services
cd docker/qdrant
docker-compose up -d
```

**4. Memory issues**
- Close other applications
- Use FAISS or ChromaDB instead of Milvus
- Process smaller PDFs

### Getting Help

1. Check the logs in the terminal
2. Verify all environments are created correctly
3. Ensure API keys are set (if using cloud services)
4. Check Docker services are running (if using Docker)

## 📚 Advanced Usage

### Custom Parsers

To add a new parser:

1. Create a new file in `parsers/`
2. Follow the existing parser structure
3. Add environment configuration if needed
4. Register in `database/run_pipeline.py`

### Custom Vector Stores

To add a new vector store:

1. Create implementation in `database/`
2. Add configuration in `config/vector_store_config.py`
3. Register in `database/vector_store_factory.py`

### Batch Processing

```bash
# Process multiple PDFs
for pdf in documents/*.pdf; do
    python -m database.run_pipeline "$pdf" "output/$(basename "$pdf" .pdf).json" --vector-store chroma
done
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision API
- Hugging Face for transformer models
- Vector database communities (ChromaDB, Qdrant, Weaviate, Milvus, FAISS)
- PDF parsing libraries (PyMuPDF, PDFPlumber, Docling, etc.)

