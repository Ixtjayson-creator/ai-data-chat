import os
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from vector_db.qdrant_client import QdrantClientHandler
from models.llama_runner import LlamaRunner
from embeddings.embedder import Embedder
from rag.retriever import Retriever
from rag.rag_pipeline import RAGPipeline
import uuid

app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for low-resource model (under 3GB setup)
MODEL_DIR = "models"
MODEL_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
# Using HuggingFace resolve URL
MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"

qdrant_handler = None
llama_runner = None
embedder = None
retriever = None
rag_pipeline = None

def download_model_if_missing():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading model {MODEL_FILENAME} (approx 400MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully!")

@app.on_event("startup")
def startup_event():
    global qdrant_handler, llama_runner, embedder, retriever, rag_pipeline
    
    # 1. Init Embedding Model and Qdrant db via embedder module
    print("Loading embedding model and Qdrant integration...")
    try:
        embedder = Embedder("all-MiniLM-L6-v2")
        qdrant_handler = embedder.qdrant
        retriever = Retriever(embedding_model=embedder.model, qdrant_handler=qdrant_handler)
    except Exception as e:
        print(f"Warning: Failed to initialize Qdrant/Embedder/Retriever ({e}). Is Qdrant running?")
    
    # 2. Load LLM (llama.cpp)
    download_model_if_missing()
    print("Initializing llama.cpp local LLM...")
    llama_runner = LlamaRunner(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)
    
    # 3. Init Unified RAG Pipeline
    rag_pipeline = RAGPipeline(retriever=retriever, llama_runner=llama_runner)
    
    print("FastAPI Backend Ready!")

class EmbedRequest(BaseModel):
    chunks: List[str]
    source: str

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    history: List[Message]

@app.get("/api/status")
def get_status():
    return {"status": "ok", "message": "FastAPI processing backend is active"}

@app.post("/upload-documents")
def upload_documents(request: EmbedRequest):
    if not embedder:
        raise HTTPException(status_code=500, detail="Embedder/Qdrant database not connected")
        
    try:
        # Pre-process requests into standardized formatting blocks before passing them
        chunks_data = []
        for i, chunk in enumerate(request.chunks):
            chunks_data.append({
                "text": chunk,
                "source": request.source,
                "metadata": {
                    "department": "general", # Just mocking metadata formatting requested by user
                    "month": "unknown",
                    "chunk_index": i
                }
            })
            
        # Using the clean Embedder wrapper specifically
        embedder.process_and_store(chunks_data)
            
        return {"status": "indexed", "chunks_processed": len(request.chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def ask_question(request: QueryRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="Backend models not completely loaded")
        
    try:
        # Run the full unified RAG pipeline
        answer = rag_pipeline.ask(question=request.query, top_k=5)
        
        return {"status": "success", "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
