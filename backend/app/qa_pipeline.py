# backend/app/qa_pipeline.py
import os
import asyncio
import pathway as pw
from dotenv import load_dotenv # type: ignore
from langchain_openai import ChatOpenAI  # type: ignore
from langchain.chains import RetrievalQA  # type: ignore
from langchain.prompts import PromptTemplate  # type: ignore
from .vector_index import load_index
from langchain_community.tools import TavilySearchResults

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

# --- Live Data Processing with Pathway ---
async def process_live_data():
    """A Pathway pipeline to process live data updates."""
    live_data = pw.io.jsonlines.read(
        "./data/live/", 
        schema=LiveDataSourceSchema, 
        mode="streaming",
        autocommit_duration_ms=1000,
    )

    # In a real application, you would add transformations and sinking here.
    # For this demo, we'll just print the data to the console.
    pw.io.printout(live_data)
    pw.run_async()

class LiveDataSourceSchema(pw.Schema):
    id: int
    content: str
    source: str

# --- QA Pipeline ---

def get_retriever(k=4):
    db = load_index()
    if db is None:
        raise RuntimeError("FAISS index not available. Run ingestion first.")
    return db.as_retriever(search_kwargs={"k": k})

def answer_question(question: str):
    search = TavilySearchResults()
    tavily_result = search.invoke(question)

    local_docs = []
    if os.path.exists("faiss_index"):
        retriever = get_retriever(k=3)
        local_docs = retriever.get_relevant_documents(question)

    evidence_parts = []
    sources = []

    if tavily_result:
        evidence_parts.append(f"[src1] {tavily_result} (source: Web Search)")
        sources.append({"id": 1, "source": "Web Search", "text": tavily_result})

    if local_docs:
        for i, d in enumerate(local_docs):
            source_id = len(evidence_parts) + 1
            evidence_parts.append(f"[src{source_id}] {d.page_content[:800]} (source: {d.metadata.get('source', 'unknown')})")
            sources.append({"id": source_id, "source": d.metadata.get("source", "local"), "text": d.page_content[:500]})

    if not evidence_parts:
        return {"answer": "I couldn't find enough information.", "sources": []}

    evidence = "\n\n".join(evidence_parts)

    template = """You are an expert research assistant, known for your bold and insightful analysis.
Given the user's question and the following evidence excerpts, produce:
1) A "bold claim" or key takeaway.
2) A concise, evidence-backed answer with inline citations [srcX].
3) A short "contrasting views" section (if applicable).
4) A confidence score (low/medium/high) and why.

Question: {question}

Evidence:
{evidence}
"""
    prompt = PromptTemplate(input_variables=["question", "evidence"], template=template)
    llm = ChatOpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)
    response = llm.invoke(prompt.format(question=question, evidence=evidence))

    return {"answer": response.content, "sources": sources}
