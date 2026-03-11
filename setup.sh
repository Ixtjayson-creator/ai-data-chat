#!/bin/bash

echo "Starting setup for DataMind Edge AI (Python + Qdrant + Llama.cpp)"

# 1. Setup Python Env
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating venv and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 2. Start Qdrant
echo "Starting Qdrant vector database on port 6333..."
if command -v docker &> /dev/null; then
    docker run -d -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z --name qdrant qdrant/qdrant:latest || docker start qdrant
else
    echo "Docker is not installed! You will need to install and run Qdrant manually on localhost:6333."
fi

# 3. Start Backend
echo "Starting FastAPI Backend..."
pkill -f uvicorn || true
echo "The backend will automatically download the 400MB LLM model on first run if it isn't found."
uvicorn main:app --host 0.0.0.0 --port 8000
