# DataMind Edge AI 🚀

A high-performance, **local AI** document intelligence platform explicitly designed to operate safely inside completely constrained memory limits (< 3GB RAM/VRAM), securely indexing and searching your knowledge base via **Qdrant** and reasoning over it using **llama.cpp (GGUF)** local LLMs.

## ✨ Key Features
- **Ultra-Lightweight Reasoning**: Natively binds and executes the `Qwen2.5-0.5B` quantized LLM natively matching highly constrained memory devices efficiently.
- **Persistent Local Embeddings**: Offloads memory-heavy array searching out of the browser and drops it securely into an ephemeral **Docker-driven Qdrant** instance scaling infinitely.
- **Smart RAG**: Robust Retrieval-Augmented Generation formatting text context properly referencing citations (e.g., `[Source: document.pdf]`).
- **Completely Private Core**: Absolutely zero outbound tracking, zero third-party internet inference API calls natively - everything resolves localhost.

## 🛠️ How to Use (Installation)

### Prerequisites
Ensure your device has installed:
- `python3` & `python3-venv`
- `docker` (For starting the Qdrant Vector database)

### Quick Start Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Ixtjayson-creator/Aidata.git
    cd Aidata
    ```
    
2. **Execute the Setup Pipeline**:
    We have provided a unified bash script that automatically compiles your sandbox, creates a virtual python environment, boots your memory-safe Qdrant database, downloads the lightweight 400MB LLM engine, and spins up the backend mapping layers.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    *(Note: This terminal window will now actively host the backend. Keep it open!)*

3.  **Start the Local Frontend UI**:
    Open a **new separate terminal window** in the exact same directory (`Aidata`), and serve the local interactive HTML panel:
    ```bash
    python3 -m http.server 8080
    ```

4.  **Open in Browser**:
    Visit `http://localhost:8080/frontend/chat.html`

5.  **Initialize & Chat**:
    - The UI Engine should immediately flip to **Online (Ready)** verifying connection to our Python API.
    - Drag and drop your documents (PDFs, CSVs, Texts) directly into the sidebar to vectorize and index them instantly into Qdrant.
    - Start asking complex analytical questions!

---

### 🛑 Stopping the Services
To completely stop the application backend, database, and UI:
1. **Stop the FastAPI Backend**: Go to the terminal that ran `./setup.sh` and press `CTRL + C`.
2. **Stop the Frontend UI**: Go to the terminal running the `python3 -m http.server` and press `CTRL + C`.
3. **Stop Qdrant Vector Database**: Run the following command in any terminal:
   ```bash
   docker stop qdrant
   ```

### 🔁 Restarting the Services (After initial setup)
If you have already installed dependencies and just need to start the application again on a new day:
1. **Start the Qdrant Database**:
   ```bash
   docker start qdrant
   ```
2. **Start the Backend APIs**:
   ```bash
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   *(Alternatively, running `./setup.sh` again is completely safe and will automatically restart everything for you!)*
3. **Start the Frontend UI**:
   ```bash
   python3 -m http.server 8080
   ```
   Then visit `http://localhost:8080/frontend/chat.html`

## 🧠 Technology Stack
- **AI Backend Router**: `FastAPI` / `Uvicorn`
- **Embedding Generation**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database**: `Qdrant` (Docker Localhost)
- **Local LLM Execution**: `llama-cpp-python` (`Qwen2.5-0.5B-Instruct-GGUF`)
- **Frontend Architecture**: Glassmorphism HTML/JS dynamically mapped exactly to REST APIs.

## 📁 Repository Structure
```text
ai-data-chat/
├── frontend/             # 🌐 Web UI & Fetch logics
│   ├── chat.html         # Document View & Interaction panel
│   ├── script.js         # Interface triggers
│   └── worker.js         # Asynchronous HTTP REST proxy mappings
├── vector_db/            # 🗄️ Qdrant wrapper classes
├── embeddings/           # 🧩 Chunking & MiniLM Vectorizing
├── models/               # 🧠 Llama.cpp generative routing & explicit logic
├── rag/                  # 🏗️ The primary RAG orchestrator unifying Qdrant & LLM
├── main.py               # 🚀 The FastAPI controller listening for frontend events
├── requirements.txt      # 📦 Setup dependencies explicitly bound to CPU
└── setup.sh              # ⚙️ Fully automated installation/verification bootstrapper
```

## 🔒 Privacy & Security
DataMind Edge AI is built with a "Privacy First" philosophy. 
- **No Data Uploads**: Your files legitimately never leave your computer's RAM/Storage.
- **Local Indexing**: Qdrant binds locally mapped securely without exposing ports globally.
- **Local Inference**: All AI "thinking" occurs transparently.

## License
MIT License
