import os
import asyncio
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import your application modules
from .qa_pipeline import answer_question, process_live_data
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
# Allow all origins for now. You can restrict this to your frontend's domain later.
origins = ["*"]

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

# ---------- File Storage Directory ----------
UPLOAD_DIR = "./data/files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Background Task for Live Data ----------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_live_data())

# ---------- Core Routes ----------

@app.post("/upload_file/")
async def upload_and_ingest_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        local_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(local_path, "wb") as f:
            f.write(content)

        build_index_from_paths([local_path])
        record_usage("report_generated", 1)

        return {
            "status": "success", 
            "filename": file.filename, 
            "message": "File uploaded and ingested successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/ask/")
async def ask_question_route(payload: QuestionRequest, db: Session = Depends(get_db)):
    record_usage("question_asked", 1)
    qa_response = answer_question(payload.question)

    if "sources" in qa_response and qa_response["sources"]:
        try:
            usage = models.ReportUsage(
                question=payload.question, 
                response=qa_response["answer"],
                credits_used=1
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)
            qa_response["report_id"] = usage.id
            record_usage("report_generated", 1)
        except Exception as e:
            print(f"Database or billing error: {e}")

    return qa_response

@app.get("/usage/")
def get_usage(db: Session = Depends(get_db)):
    questions_asked = db.query(models.ReportUsage).count()
    reports_generated = db.query(models.ReportUsage).count() # Simplified for now
    return {"questions_asked": questions_asked, "reports_generated": reports_generated}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
