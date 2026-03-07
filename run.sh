#!/bin/bash
# A simple script to start the AI Data Chat backend API

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to the current directory so modules can be imported
export PYTHONPATH="$DIR:$PYTHONPATH"

# Kill any existing process on port 8000
echo "Checking for existing server processes..."
existing_pid=$(ss -lptn 'sport = :8000' 2>/dev/null | awk 'NR>1 {print $6}' | awk -F'pid=' '{print $2}' | awk -F',' '{print $1}')
if [ ! -z "$existing_pid" ]; then
    echo "Killing existing server on port 8000 (PID: $existing_pid)"
    kill -9 $existing_pid
fi

echo "Starting FastAPI server..."
"$DIR/venv/bin/python3" "$DIR/backend/main.py"
