from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from backend.main import process_file_and_chat

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/chat")
async def chat_with_data(file: UploadFile = File(...), question: str = Form(...)):
    """
    Endpoint to upload a file and ask a question in one go.
    Stores the file temporarily, processes it, and returns the LLM response.
    """
    try:
        # 1. Save uploaded file
        file_ext = os.path.splitext(file.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Process with RAG Pipeline
        logging_info = f"Processing query for {file.filename}"
        print(logging_info)
        
        answer = process_file_and_chat(file_path, question)
        
        # 3. Clean up temp file (optional, but good practice)
        # os.remove(file_path)
        
        return {
            "filename": file.filename,
            "question": question,
            "answer": answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Data Chat API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
