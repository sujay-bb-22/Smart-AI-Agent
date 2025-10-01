from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_upload_pdf():
    """Test uploading a PDF file."""
    with open("dummy.pdf", "wb") as f:
        f.write(b"dummy content")
    with open("dummy.pdf", "rb") as f:
        response = client.post("/upload_pdf/", files={"file": ("dummy.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert response.json() == {"filename": "dummy.pdf", "location": "./data/pdfs/dummy.pdf"}

def test_ask_question():
    """Test asking a question."""
    response = client.post("/ask/", json={"question": "What is the meaning of life?"})
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the meaning of life?"
    assert "answer" in data
    assert "report_id" in data

def test_get_usage():
    """Test getting the usage count."""
    response = client.get("/usage/")
    assert response.status_code == 200
    assert "reports_generated" in response.json()

def test_ingest_pdf():
    """Test ingesting a PDF file."""
    with open("dummy2.pdf", "wb") as f:
        f.write(b"dummy content")
    with open("dummy2.pdf", "rb") as f:
        response = client.post("/ingest/", files={"file": ("dummy2.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "filename": "dummy2.pdf"}
