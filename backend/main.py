import os
import shutil
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our modular components
from loaders.csv_loader import load_csv
from loaders.excel_loader import load_excel
from loaders.pdf_loader import load_pdf
from backend.rag_pipeline import index_document, retrieve_context
from backend.llm_runner import generate_answer
from vector_store.faiss_store import clear_store

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="DataMind AI Chat API",
    description="Production-ready RAG API for document intelligence",
    version="1.0.0"
)

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = []

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads and indexes a document. 
    Supports PDF, CSV, and Excel.
    """
    file_path = None
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_id = uuid.uuid4().hex[:8]
        temp_filename = f"{unique_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logging.info(f"Processing upload: {file.filename} ({file_ext})")
        
        content = ""
        if file_ext == '.csv':
            content = load_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            content = load_excel(file_path)
        elif file_ext == '.pdf':
            content = load_pdf(file_path)
        else:
            if os.path.exists(file_path): os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Unsupported format: {file_ext}")

        if not content or content.startswith("Error"):
            if os.path.exists(file_path): os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Data Extraction Error: {content}")

        # Index the document with its source name
        index_document(content, source=file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "message": "Intelligence engine updated with new data."
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Upload failure: {e}")
        if file_path and os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint with conversation memory.
    """
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Retrieve context from multiple indexed docs
        context = retrieve_context(request.question)
        
        # Generate insight
        logging.info("Generating intelligence report...")
        answer = generate_answer(context, request.question, request.history)
        
        return {
            "question": request.question,
            "answer": answer,
            "has_context": bool(context)
        }
        
    except Exception as e:
        logging.error(f"Inquiry error: {e}")
        raise HTTPException(status_code=500, detail="Insight generation failed")

@app.post("/clear")
async def clear_data():
    """Wipes the vector store and any temporary files."""
    try:
        clear_store()
        # Clean uploads folder
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')
        return {"status": "success", "message": "Environment reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "active", 
        "engine": "Ollama/Qwen-2.5-3B",
        "service": "DataMind RAG Service"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
