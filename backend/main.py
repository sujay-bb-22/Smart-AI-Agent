# backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn # type: ignore
from backend.app.qa_pipeline import answer_question
from backend.app.pdf_ingest import process_pdf
from backend.app.vector_index import add_documents_to_index

# --- App Initialization ---
app = FastAPI()

# --- CORS Configuration ---
# Allows all origins for Vercel deployment. 
# For production, you might want to restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)


# --- API Endpoints ---

# Vercel will route /api requests to this app.
# The path here is relative to that, so it becomes /api/qa/
@app.post("/api/qa/")
async def ask_question(request: dict):
    question = request.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question not provided")
    
    try:
        result = answer_question(question)
        return result
    except Exception as e:
        # Providing more specific error details can be helpful for debugging
        raise HTTPException(status_code=500, detail=f"Error in QA pipeline: {str(e)}")

# This becomes /api/upload/
@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")
    
    # Note: Vercel has a temporary filesystem. This upload will not persist.
    temp_file_path = f"/tmp/{file.filename}" # Use /tmp directory for Vercel
    try:
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process the PDF to get documents
        documents = process_pdf(temp_file_path)
        
        # Add documents to the in-memory vector index
        add_documents_to_index(documents)
        
        return {"message": "File uploaded and processed successfully for this session."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        # Clean up the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Optional: A root endpoint for testing the API deployment
@app.get("/api/health")
def health_check():
    return {"status": "Backend is running"}
