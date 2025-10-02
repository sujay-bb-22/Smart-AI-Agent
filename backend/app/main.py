import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import your application modules
from .qa_pipeline import answer_question
from .billing import record_usage
from .database import SessionLocal, engine
from . import models
from .vector_index import build_index_from_paths

# ---------- Database ----------
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- FastAPI app ----------
app = FastAPI(title="Smart Research Assistant")

# ---------- CORS Middleware ----------
origins = [
    "http://localhost:3000",
    "https://frontend-4mzl.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health Check ----------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ---------- Request Models ----------
class QuestionRequest(BaseModel):
    question: str

# ---------- PDF Storage Directory ----------
# This is the correct, permanent location for uploaded PDFs
UPLOAD_DIR = "./data/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Core Routes ----------

@app.post("/upload_pdf/")
async def upload_and_ingest_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF file, saves it to a permanent location, and immediately
    ingests its content into the vector index.
    """
    try:
        # Read the content of the uploaded file
        content = await file.read()

        # Save the file to the correct permanent directory
        local_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(local_path, "wb") as f:
            f.write(content)

        # Immediately ingest the document into the index
        build_index_from_paths([local_path])

        return {
            "status": "success", 
            "filename": file.filename, 
            "message": "File uploaded and ingested successfully."
        }
    except Exception as e:
        # If anything goes wrong, return a detailed error message
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/ask/")
async def ask_question_route(payload: QuestionRequest, db: Session = Depends(get_db)):
    """
    Receives a question, gets an answer from the QA pipeline, and records usage.
    """
    # Get the answer from the QA pipeline
    qa_response = answer_question(payload.question)

    # Record usage in the database (if an actual answer is generated)
    if "sources" in qa_response and qa_response["sources"]:
        try:
            record_usage(question=payload.question, credits=1) # Example credit usage
            usage = models.ReportUsage(question=payload.question, response=qa_response["answer"])
            db.add(usage)
            db.commit()
            db.refresh(usage)
            qa_response["report_id"] = usage.id
        except Exception as e:
            print(f"Database or billing error: {e}")

    return qa_response

@app.get("/usage/")
def get_usage(db: Session = Depends(get_db)):
    """
    Returns the total number of reports generated.
    """
    count = db.query(models.ReportUsage).count()
    return {"reports_generated": count}
