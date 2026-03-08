# DataMind Edge AI 🚀

A high-performance, **completely serverless** document intelligence platform that runs entirely in your browser. Using `Transformers.js` and modern web technologies, DataMind Edge AI provides a private, secure, and fast way to analyze your documents without ever sending data to a server.

## ✨ Key Features
- **Browser-Native AI**: Powered by `HuggingFace Transformers.js (v3)` with WebGPU acceleration.
- **Zero-Backend**: No Python, no node.js, and no database required. It's just HTML, CSS, and JavaScript.
- **Absolute Privacy**: Your documents are processed, indexed, and queried entirely on your local machine.
- **Smart RAG**: Robust Retrieval-Augmented Generation that supports PDF, CSV, and Excel formats.
- **Source Citations**: The AI cites specific files (e.g., `[Source: data.csv]`) for every claim it makes.
- **Hardware Agnostic**: Automatically falls back to high-performance WASM if WebGPU is not supported by your browser/hardware.

## 🛠️ How to Use

### Quick Start (The Easiest Way)
Because the app uses Web Workers, browsers require it to be served over a local server (even though there is no code running on that server).

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Ixtjayson-creator/Aidata.git
    cd Aidata
    ```
2.  **Start a local server**:
    ```bash
    # If you have Python:
    python3 -m http.server 8080
    ```
3.  **Open in Browser**:
    Visit `http://localhost:8080/frontend/chat.html`

4.  **Initialize & Chat**:
    - Wait a few seconds for the AI engine to download (it will be cached for future use).
    - Upload your documents in the sidebar.
    - Start asking questions!

## 🧠 Technology Stack
- **AI Core**: `Transformers.js` (Hugging Face)
- **Embedding Model**: `Xenova/bge-small-en-v1.5` (~100MB)
- **LLM Reasoning**: `onnx-community/Qwen2.5-0.5B-Instruct` (4-bit quantization)
- **Processing**: WebGPU (Primary) / WASM (Fallback)
- **Loaders**: `PDF.js`, `PapaParse`, `SheetJS`
- **UI Architecture**: Glassmorphism CSS with `Marked.js` and `Highlight.js`

## 📁 Repository Structure
```text
ai-data-chat/
├── frontend/           # The entire application logic
│   ├── chat.html       # UI Layout & Design
│   ├── script.js       # Main controller & UI logic
│   └── worker.js       # The AI Intelligence Engine (Web Worker)
└── README.md
```

## 🔒 Privacy & Security
DataMind Edge AI is built with a "Privacy First" philosophy. 
- **No Data Uploads**: Your files never leave your computer.
- **Local Indexing**: The vector store is created in the browser's temporary memory.
- **Local Inference**: All AI "thinking" happens on your GPU/CPU.

## License
MIT License
