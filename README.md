# DataMind Edge AI 🚀

A high-performance, **serverless** document intelligence platform that runs entirely in your browser. No data ever leaves your machine—even the AI reasoning is local.

## ✨ Key Features
- **Browser-Native AI**: Powered by `Transformers.js` (WebGPU accelerated).
- **Zero-Backend**: No server required. Simply open `chat.html`.
- **Absolute Privacy**: Documents are indexed and queried in your browser's private memory.
- **Smart RAG**: Supports PDF, CSV, and Excel with semantic chunking and source citations.
- **Enterprise UI**: Premium glassmorphism design with professional markdown rendering.

## 🛠️ How to Use
1.  **Open** the `frontend/chat.html` file in any modern browser (Chrome/Edge recommended for WebGPU).
2.  **Wait** a few seconds for the AI Intelligence engine to initialize (first-time download is ~150MB).
3.  **Upload** your documents in the sidebar.
4.  **Chat** with your data!

## 🧠 Technology Stack
- **AI Core**: Transformers.js (v2/v3).
- **Models**: BGE-Small (Embeddings) + Qwen-2.5 0.5B (Quantized LLM).
- **Loaders**: PDF.js, PapaParse, SheetJS.
- **Highlighter**: Highlight.js & Marked.

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
