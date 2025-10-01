import { useState } from "react";
import { askQuestion } from "../api";

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question) return;
    try {
      const res = await askQuestion(question);
      setAnswer(res.answer);
    } catch (err) {
      console.error(err);
      setAnswer("Error: Could not get answer.");
    }
  };

  return (
    <div>
      <h2>Ask a Question</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question"
          style={{ width: "300px" }}
          required
        />
        <button type="submit" style={{ marginLeft: "10px" }}>Ask</button>
      </form>
      {answer && (
        <div style={{ marginTop: "20px" }}>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
