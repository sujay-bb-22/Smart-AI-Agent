# backend/app/qa_pipeline.py
import os
from dotenv import load_dotenv # type: ignore
from langchain_openai import ChatOpenAI  # type: ignore
from langchain.chains import RetrievalQA  # type: ignore
from langchain.prompts import PromptTemplate  # type: ignore
from .vector_index import load_index
from langchain_community.tools import TavilySearchResults
from unstructured.partition.auto import partition


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
    # 1. Always perform a web search
    search = TavilySearchResults()
    tavily_result = search.invoke(question)

    local_docs = []
    # 2. Also search local documents if available
    if os.path.exists("faiss_index"):
        retriever = get_retriever(k=3) # get fewer docs to balance with web search
        local_docs = retriever.get_relevant_documents(question)

    # 3. Combine evidence
    evidence_parts = []
    sources = []

    # Add web search result as evidence
    if tavily_result:
        evidence_parts.append(f"[src1] {tavily_result} (source: Web Search)")
        sources.append({"id": 1, "source": "Web Search", "text": tavily_result})

    # Add local docs as evidence
    if local_docs:
        for i, d in enumerate(local_docs):
            source_id = len(evidence_parts) + 1
            evidence_parts.append(f"[src{source_id}] {d.page_content[:800]} (source: {d.metadata.get('source', 'unknown')})")
            sources.append({"id": source_id, "source": d.metadata.get("source", "local"), "text": d.page_content[:500]})

    if not evidence_parts:
        return {
            "answer": "I couldn't find any information on that topic. Please try rephrasing your question.",
            "sources": []
        }

    evidence = "\n\n".join(evidence_parts)

    # 4. Generate response with the "bold claim" prompt
    template = """You are an expert research assistant, known for your bold and insightful analysis.
Given the user's question and the following evidence excerpts from the web and/or local documents, produce:
1) A "bold claim" or key takeaway from your research.
2) A concise, evidence-backed answer with inline citations [srcX].
3) A short "contrasting views" section (if applicable).
4) A confidence score (low/medium/high) and why.

Question: {question}

Evidence:
{evidence}
"""

    prompt = PromptTemplate(input_variables=["question", "evidence"], template=template)

    llm = ChatOpenAI(
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )

    response = llm.invoke(prompt.format(question=question, evidence=evidence))

    return {"answer": response.content, "sources": sources}
