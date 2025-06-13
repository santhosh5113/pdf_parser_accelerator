FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install core dependencies first
RUN pip install --no-cache-dir \
    numpy>=1.25.0 \
    faiss-cpu==1.11.0 \
    sentence-transformers>=2.5.0 \
    torch>=2.1.2

# Copy requirements and install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/faiss_index /app/uploads /app/processed

# Set environment variables
ENV PYTHONPATH=/app
ENV VECTOR_STORE_TYPE=faiss
ENV FAISS_INDEX_PATH=/app/faiss_index
ENV EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Copy application code
COPY . .

# Set permissions
RUN chmod -R 777 /app/faiss_index /app/uploads /app/processed

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 