import React, { useState } from 'react';

function AskForm({ onNewAnswer }) {
  const [question, setQuestion] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      const response = await fetch('https://ai-agent-backend-9wj4.onrender.com/api/qa/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      onNewAnswer(data);
      setError(null);
    } catch (error) {
      setError('Error fetching answer.');
      console.error('There was an error!', error);
    }

    setQuestion('');
  };

  return (
    <div className="input-area">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What is AI?"
        />
        <button type="submit">Ask</button>
      </form>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default AskForm;
