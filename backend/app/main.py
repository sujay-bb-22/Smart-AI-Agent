import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from .pdf_ingest import save_file_locally, upload_to_s3, USE_S3
from .qa_pipeline import answer_question
from .billing import record_usage
from .database import SessionLocal, engine
from . import models

# ---------- Database ----------
models.Base.metadata.create_all(bind=engine)

def get_db():
    """Provide a database session to path operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- FastAPI app ----------
app = FastAPI(title="Smart Research Assistant")

# ---------- CORS Middleware ----------
# In production, you should restrict this to your frontend's domain
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

# ---------- Upload Directory ----------
UPLOAD_DIR = "./data/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Routes ----------

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF to local storage or S3.
    
    Returns:
        dict: filename and storage location
    """
    content = await file.read()
    local_path = save_file_locally(content, file.filename)
    if USE_S3:
        key = f"pdfs/{file.filename}"
        url = upload_to_s3(local_path, key)
    else:
        url = local_path
    return {"filename": file.filename, "location": url}

@app.post("/ask/")
async def ask_question(payload: QuestionRequest, db: Session = Depends(get_db)):
    print("✅ Received question:", payload.question)
    
    try:
        answer = answer_question(payload.question)
        print("✅ Answer generated:", answer)
    except Exception as e:
        print("❌ Error in answer_question:", e)
        return {"error": "answer_question failed", "details": str(e)}

    try:
        record_usage(question=payload.question, credits=1)
        print("✅ Usage recorded")
    except Exception as e:
        print("❌ Error in record_usage:", e)
        return {"error": "record_usage failed", "details": str(e)}

    try:
        usage = models.ReportUsage(
            question=payload.question,
            response=answer
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
        print("✅ Usage saved in DB, ID:", usage.id)
    except Exception as e:
        print("❌ DB error:", e)
        return {"error": "database save failed", "details": str(e)}

    return {"question": payload.question, "answer": answer, "report_id": usage.id}


@app.get("/usage/")
def get_usage(db: Session = Depends(get_db)):
    """
    Get total number of reports generated.

    Returns:
        dict: count of reports
    """
    count = db.query(models.ReportUsage).count()
    return {"reports_generated": count}


@app.post("/ingest/")
async def ingest_pdf(file: UploadFile = File(...), x_api_key: str = Header(None)):
    # Optional: require an API key header in production
    if os.getenv("INGEST_API_KEY") and x_api_key != os.getenv("INGEST_API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # save file locally
    local_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(local_path, "wb") as f:
        f.write(await file.read())

    # build index from this file (you can also pass multiple files)
    from .vector_index import build_index_from_paths
    build_index_from_paths([local_path])
    return {"status": "ok", "filename": file.filename}
