# backend/app/qa_pipeline.py
import os
from dotenv import load_dotenv # type: ignore
from langchain_openai import ChatOpenAI  # type: ignore
from langchain.chains import RetrievalQA  # type: ignore
from langchain.prompts import PromptTemplate  # type: ignore
from .vector_index import load_index

# Load environment variables from .env file
load_dotenv()

# Get API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in your .env file or system environment.")

def get_retriever(k=4):
    db = load_index()
    if db is None:
        raise RuntimeError("FAISS index not available. Run ingestion first.")
    retriever = db.as_retriever(search_kwargs={"k": k})
    return retriever

def answer_question(question: str):
    retriever = get_retriever(k=6)

    # Retrieve top docs
    docs = retriever.get_relevant_documents(question)

    # Build a multi-perspective prompt
    template = """You are an expert research assistant.
Given the user's question and the following evidence excerpts, produce:
1) A concise, evidence-backed answer with inline citations [srcX].
2) A short "contrasting views" section (if applicable).
3) A confidence score (low/medium/high) and why.

Question: {question}

Evidence:
{evidence}
"""
    evidence = "\n\n".join([
        f"[src{i+1}] {d.page_content[:800]} (source: {d.metadata.get('source', 'unknown')})"
        for i, d in enumerate(docs)
    ])

    prompt = PromptTemplate(input_variables=["question", "evidence"], template=template)

    # Pass API key explicitly to ChatOpenAI
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )

    response = llm(prompt.format(question=question, evidence=evidence))

    # Return text and a small list of sources for clickable evidence
    sources = [
        {"id": i+1, "source": d.metadata.get("source", "local"), "text": d.page_content[:500]}
        for i, d in enumerate(docs)
    ]
    return {"answer": response.content, "sources": sources}
