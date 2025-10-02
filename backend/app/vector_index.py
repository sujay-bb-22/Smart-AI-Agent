# backend/app/vector_index.py
import os
from langchain_community.document_loaders import PyPDFLoader  # type: ignore
from langchain_openai import OpenAIEmbeddings  # type: ignore
from langchain_community.vectorstores import FAISS  # type: ignore
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in your .env file.")

INDEX_DIR = os.getenv("INDEX_DIR", "./faiss_index")

def build_index_from_paths(pdf_paths: list, index_dir=INDEX_DIR):
    """
    Build a FAISS vector index from given PDF files.
    """
    docs = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        docs.extend(loader.load())

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    faiss_db = FAISS.from_documents(docs, embeddings)

    # Save FAISS index locally
    faiss_db.save_local(index_dir)
    return faiss_db

def load_index(index_dir=INDEX_DIR):
    """
    Load an existing FAISS index from disk.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    if os.path.exists(index_dir):
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    return None
