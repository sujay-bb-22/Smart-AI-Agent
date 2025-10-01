import React, { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
  const [usage, setUsage] = useState(0);

  // Ask question API call
  const askQuestion = async () => {
    if (!question) return;
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/ask/?question=${encodeURIComponent(question)}`
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
      const res = await fetch("http://127.0.0.1:8000/usage/");
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
      const res = await fetch("http://127.0.0.1:8000/upload_pdf", {
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
        <h2>Ask your question:</h2>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here..."
        />
        <button onClick={askQuestion}>Ask</button>

        {answer && <div className="answer-box">{answer}</div>}

        <div className="upload-box">
          <h3>Upload PDF:</h3>
          <input type="file" accept=".pdf" onChange={handleFileChange} />
          <button onClick={uploadPdf} style={{ marginTop: "10px" }}>
            Upload
          </button>
        </div>

        <footer>
          Reports generated: <strong>{usage}</strong>
        </footer>
      </div>
    </div>
  );
}

export default App;
