import React, { useState } from "react";
import "./App.css";

// Use the environment variable for the API URL
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
  const [usage, setUsage] = useState(0);
  const [inputType, setInputType] = useState("text"); // 'text' or 'file'

  // Ask question API call
  const askQuestion = async () => {
    if (!question) return;
    try {
      // Construct the full API URL
      const res = await fetch(
        `${API_URL}/ask/?question=${encodeURIComponent(question)}`
      );
      const data = await res.json();
      setAnswer(data.answer || JSON.stringify(data));
      fetchUsage(); // refresh usage counter
    } catch (err) {
      setAnswer("Error fetching answer.");
    }
  };

  // Fetch usage API call
  const fetchUsage = async () => {
    try {
      // Construct the full API URL
      const res = await fetch(`${API_URL}/usage/`);
      const data = await res.json();
      setUsage(data.reports_generated || 0);
    } catch (err) {
      console.log("Error fetching usage:", err);
    }
  };

  // Handle PDF file select
  const handleFileChange = (e) => {
    setPdfFile(e.target.files[0]);
  };

  // Upload PDF API call
  const uploadPdf = async () => {
    if (!pdfFile) return;
    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      // Construct the full API URL
      const res = await fetch(`${API_URL}/upload_pdf`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      alert(`PDF uploaded: ${data.filename}`);
    } catch (err) {
      alert("Error uploading PDF.");
    }
  };

  // Fetch usage when component mounts
  React.useEffect(() => {
    fetchUsage();
  }, []);

  return (
    <div className="App">
      <header className="App-header">Smart Research Assistant 🚀</header>

      <div className="container">
        <h2>Analyze Data</h2>
        <div className="input-selection">
          <select value={inputType} onChange={(e) => setInputType(e.target.value)}>
            <option value="text">Ask a Question</option>
            <option value="file">Upload a PDF</option>
          </select>
        </div>

        {inputType === 'text' ? (
          <div className="input-area">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question here..."
            />
            <button onClick={askQuestion}>Ask</button>
          </div>
        ) : (
          <div className="input-area">
            <input type="file" accept=".pdf" onChange={handleFileChange} />
            <button onClick={uploadPdf} style={{ marginTop: "10px" }}>
              Upload
            </button>
          </div>
        )}

        {answer && <div className="answer-box">{answer}</div>}

        <footer>
          Reports generated: <strong>{usage}</strong>
        </footer>
      </div>
    </div>
  );
}

export default App;
