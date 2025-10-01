from sqlalchemy import Column, Integer, String, DateTime, func # type: ignore
from .database import Base   # make sure Base is imported here

class ReportUsage(Base):
    __tablename__ = "report_usage"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    response = Column(String, nullable=True)
    report_type = Column(String, default="basic")
    credits_used = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
