#!/bin/bash
# AI Data Chat Launcher

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$DIR:$PYTHONPATH"

echo "=== DataMind AI Chat Startup ==="

# 1. Kill existing processes on port 8000
echo "[1/4] Checking for existing server processes..."
existing_pid=$(ss -lptn 'sport = :8000' 2>/dev/null | awk 'NR>1 {print $6}' | awk -F'pid=' '{print $2}' | awk -F',' '{print $1}')
if [ ! -z "$existing_pid" ]; then
    echo "Killing existing server on port 8000 (PID: $existing_pid)"
    kill -9 $existing_pid
fi

# 2. Check for Ollama and the model
echo "[2/4] Verifying Ollama and Model (qwen2.5:3b)..."
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is not installed. Please install it from https://ollama.com"
    exit 1
fi

if ! ollama list | grep -q "qwen2.5:3b"; then
    echo "Model qwen2.5:3b not found. Pulling it now... (this may take a minute)"
    ollama pull qwen2.5:3b
fi

# 3. Check Virtual Environment
echo "[3/4] Verifying Virtual Environment..."
if [ ! -f "$DIR/venv/bin/python3" ]; then
    echo "Virtual environment not found. Creating it..."
    python3 -m venv "$DIR/venv"
    "$DIR/venv/bin/pip" install fastapi uvicorn faiss-cpu sentence-transformers pypdf pandas openpyxl pdfminer.six requests
fi

# 4. Start Server
echo "[4/4] Starting FastAPI server..."
"$DIR/venv/bin/python3" "$DIR/backend/main.py"
