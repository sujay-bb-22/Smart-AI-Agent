# backend/app/billing.py
from .database import SessionLocal
from .models import ReportUsage

def record_usage(question: str, credits: int = 1, metadata: dict = None):
    db = SessionLocal()
    try:
        usage = ReportUsage(
            question=question,
            credits_used=credits,
            report_type=metadata.get("type", "basic") if metadata else "basic",
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
        return usage.id
    finally:
        db.close()
