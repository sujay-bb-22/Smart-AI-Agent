# backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn # type: ignore
from backend.app.qa_pipeline import answer_question
from backend.app.pdf_ingest import process_pdf
from backend.app.vector_index import add_documents_to_index
from starlette.responses import FileResponse

# --- App Initialization ---
app = FastAPI()

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
    "http://localhost",
    "https://your-app-name.onrender.com" # Replace with your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Endpoints ---
@app.post("/api/qa/")
async def ask_question(request: dict):
    question = request.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question not provided")
    
    try:
        result = answer_question(question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")
    
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process the PDF to get documents
        documents = process_pdf(temp_file_path)
        
        # Add documents to the vector index
        add_documents_to_index(documents)
        
        return {"message": "File uploaded and processed successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        # Clean up the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Static Files and Root ---
# This must be after all other API routes
app.mount("/", StaticFiles(directory="frontend/build"), name="static")

@app.get("/{catch_all:path}")
async def serve_react_app(catch_all: str):
    return FileResponse('frontend/build/index.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
