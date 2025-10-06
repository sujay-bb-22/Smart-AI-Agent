# backend/app/qa_pipeline.py
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from .vector_index import get_retriever
import os

# Initialize the language model
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", 
    temperature=0,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

def answer_question(question: str):
    """Answers a question using the QA pipeline."""
    retriever = get_retriever()
    
    # Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    
    # Run the chain
    result = qa_chain.run(question)
    return {"answer": result}
