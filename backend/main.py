# backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn # type: ignore
from backend.app.qa_pipeline import answer_question
from backend.app.pdf_ingest import process_pdf
from backend.app.vector_index import add_documents_to_index, store

# --- Database Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup.
    # It connects to the database and ensures the pgvector extension is enabled.
    from sqlalchemy import text
    
    # The database connection is managed by the 'store' object
    with store.connect() as connection:
        # Enable the pgvector extension
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        connection.commit()
    yield
    # This code runs on shutdown if needed.

# --- App Initialization ---
app = FastAPI(lifespan=lifespan)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- API Endpoints ---

@app.post("/api/qa/")
async def ask_question_endpoint(request: dict):
    question = request.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question not provided")
    
    try:
        result = answer_question(question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/")
async def upload_file_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Use a temporary path for processing
    temp_file_path = f"/tmp/{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process the PDF into documents
        documents = process_pdf(temp_file_path)
        
        # Add documents to the persistent database index
        add_documents_to_index(documents)
        
        return {"message": f"File '{file.filename}' uploaded and processed successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/api/health")
def health_check():
    return {"status": "Backend is running"}
