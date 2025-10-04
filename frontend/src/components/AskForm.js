import React, { useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function AskForm({ onNewAnswer }) {
  const [question, setQuestion] = useState("");

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
      onNewAnswer(data);
    } catch (err) {
      onNewAnswer({ answer: "Error fetching answer." });
    }
  };

  return (
    <div className="input-area">
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={askQuestion}>Ask</button>
    </div>
  );
}

export default AskForm;
