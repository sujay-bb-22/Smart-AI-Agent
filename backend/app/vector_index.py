# backend/app/vector_index.py
import os
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings.openai import OpenAIEmbeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Database Connection ---
# The DATABASE_URL will be provided by Render's environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# The collection name is used to store the vectors in the database
COLLECTION_NAME = "smart_ai_agent_vectors"

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))

# --- PGVector Store ---
# This object will be our primary interface for interacting with the database
store = PGVector(
    connection_string=DATABASE_URL,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)


def get_retriever():
    """Returns a retriever for the vector store."""
    return store.as_retriever()

def add_documents_to_index(documents):
    """Adds a list of documents to the vector store."""
    # The add_documents function will handle embedding and storing the documents
    store.add_documents(documents)
