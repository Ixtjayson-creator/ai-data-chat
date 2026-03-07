# AI Data Chat

AI Data Chat is a Retrieval-Augmented Generation (RAG) pipeline and FastAPI backend that allows users to chat with their data from various file formats like PDF, CSV, and Excel. 

## Features
- **Multi-format Support**: Ingest data from PDF, CSV, and Excel files.
- **RAG Pipeline**: Efficiently retrieves relevant context from your documents to provide accurate answers.
- **FastAPI Backend**: A high-performance, asynchronous backend for handling requests and data processing.
- **Interactive Frontend**: Simple and intuitive web-based chat interface.
- **Session Support**: Manage interactive chat sessions with historical context.

## Project Structure
```text
ai-data-chat/
├── backend/            # RAG pipeline logic and FastAPI app
│   ├── api.py          # API endpoints
│   ├── chunking.py     # Document text chunking
│   ├── embedding.py    # Vector embeddings generation
│   ├── llm_runner.py   # LLM interaction layer
│   └── rag_pipeline.py # Main RAG process
├── frontend/           # Web-based chat interface
│   ├── chat.html
│   └── script.js
├── loaders/            # Custom data loaders for various file types
│   ├── pdf_loader.py
│   ├── csv_loader.py
│   └── excel_loader.py
└── run.sh              # Quick start script
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- [Optional] Virtual environment-aware terminal

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ixtjayson-creator/Aidata.git
   cd Aidata
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   *(Ensure you have a `requirements.txt` or install the packages manually)*
   ```bash
   pip install fastapi uvicorn faiss-cpu sentence-transformers pypdf pandas openpyxl
   ```

4. **Prepare directories**:
   The app uses `uploads/` for documents and `vector_store/` for index storage.
   ```bash
   mkdir uploads vector_store
   ```

### Running the Application
Use the provided `run.sh` script or launch manually:
```bash
./run.sh
```
Or:
```bash
python -m backend.main
```
The backend will be available at `http://localhost:8000`. You can open `frontend/chat.html` in your browser to start chatting!

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
MIT License
