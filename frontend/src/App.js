import React, { useState } from "react";
import "./App.css";

// Use the environment variable for the API URL
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [file, setFile] = useState(null);
  const [usage, setUsage] = useState(0);
  const [inputType, setInputType] = useState("text"); // 'text' or 'file'

  // Ask question API call
  const askQuestion = async () => {
    if (!question) return;
    try {
      const res = await fetch(`${API_URL}/ask/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
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

  // Handle file select
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Upload file API call
  const uploadFile = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Construct the full API URL
      const res = await fetch(`${API_URL}/upload_file/`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      alert(`File uploaded: ${data.filename}`);
    } catch (err) {
      alert("Error uploading file.");
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
            <option value="file">Upload a File</option>
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
            <input type="file" onChange={handleFileChange} />
            <button onClick={uploadFile} style={{ marginTop: "10px" }}>
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
