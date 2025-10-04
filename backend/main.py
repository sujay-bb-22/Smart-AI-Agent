# backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn # type: ignore
from app.qa_pipeline import answer_question
from app.ingestion_pipeline import process_pdf
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
    
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Start background task for ingestion
        process_pdf(temp_file_path)
        
        return {"message": "File received. Ingestion started in the background."}
    
    except Exception as e:
        # Clean up the temp file in case of an error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

# --- Static Files and Root ---
# This must be after all other API routes
app.mount("/", StaticFiles(directory="frontend/build"), name="static")

@app.get("/{catch_all:path}")
async def serve_react_app(catch_all: str):
    return FileResponse('frontend/build/index.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
