import os
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, declarative_base # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sra.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
