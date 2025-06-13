#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <vector_store>"
    echo "Available vector stores:"
    echo "  - faiss"
    echo "  - milvus"
    echo "  - weaviate (coming soon)"
    echo "  - qdrant (coming soon)"
    exit 1
}

# Check if vector store argument is provided
if [ -z "$1" ]; then
    usage
fi

# Convert to lowercase
VECTOR_STORE=$(echo "$1" | tr '[:upper:]' '[:lower:]')

# Stop any running containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null
docker-compose -f docker/faiss/docker-compose.yml down 2>/dev/null
docker-compose -f docker/milvus/docker-compose.yml down 2>/dev/null

# Switch based on vector store
case $VECTOR_STORE in
    "faiss")
        echo "Starting FAISS configuration..."
        docker-compose -f docker/faiss/docker-compose.yml up --build
        ;;
    "milvus")
        echo "Starting Milvus configuration..."
        docker-compose -f docker/milvus/docker-compose.yml up --build
        ;;
    "weaviate")
        echo "Weaviate configuration coming soon..."
        exit 1
        ;;
    "qdrant")
        echo "Qdrant configuration coming soon..."
        exit 1
        ;;
    *)
        echo "Unknown vector store: $VECTOR_STORE"
        usage
        ;;
esac 