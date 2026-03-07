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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="DataMind AI Chat API")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    1. Upload file
    2. Detect file type
    3. Load file using appropriate loader
    4. Index document into RAG pipeline
    """
    try:
        # Save file to uploads directory
        file_ext = os.path.splitext(file.filename)[1].lower()
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Detect type and load content
        content = ""
        logging.info(f"Loading {file.filename} using {file_ext} loader")
        
        if file_ext == '.csv':
            content = load_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            content = load_excel(file_path)
        elif file_ext == '.pdf':
            content = load_pdf(file_path)
        else:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")

        if not content or content.startswith("Error"):
            os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to load file content: {content}")

        # Index the document
        logging.info("Indexing document...")
        index_document(content)
        
        return {
            "status": "success",
            "filename": file.filename,
            "message": "File indexed successfully"
        }
        
    except Exception as e:
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    1. Receive user question
    2. Retrieve context from FAISS
    3. Generate AI answer using LLM
    """
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="Question is required")

        # Retrieve relevant chunks as context
        logging.info(f"Retrieving context for: {request.question}")
        context = retrieve_context(request.question)
        
        if not context:
            return {
                "answer": "I couldn't find any relevant information in the uploaded document to answer that question.",
                "context_found": False
            }

        # Generate answer using LLM runner
        logging.info("Generating AI response...")
        answer = generate_answer(context, request.question, request.history)
        
        return {
            "question": request.question,
            "answer": answer,
            "context_found": True
        }
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "online", "model": "Qwen 0.5B"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
