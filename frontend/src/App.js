import React, { useState } from "react";
import "./App.css";
import AskForm from "./components/AskForm";
import UploadPDF from "./components/UploadPDF";
import UsageDashboard from "./components/UsageDashboard";

function App() {
  const [answer, setAnswer] = useState(null);
  const [showSources, setShowSources] = useState(false);

  const handleNewAnswer = (newAnswer) => {
    setAnswer(newAnswer);
  };

  const renderAnswer = () => {
    if (!answer) return null;

    const parts = answer.answer.split(/(\n|\d\))/).filter(part => part.trim());

    return (
      <div className="answer-box">
        {parts.map((part, index) => {
          if (part.match(/^\d\)/)) {
            return <h3 key={index}>{part}</h3>;
          } else if (part === "\n") {
            return <br key={index} />;
          }
          return <p key={index}>{part}</p>;
        })}

        {answer.sources && answer.sources.length > 0 && (
          <div className="citations">
            <button onClick={() => setShowSources(!showSources)}>
              {showSources ? "Hide Sources" : "Show Sources"}
            </button>
            {showSources && (
              <ul>
                {answer.sources.map((source) => (
                  <li key={source.id}>
                    [src{source.id}] {source.source}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">Smart Research Assistant 🚀</header>

      <div className="container">
        <div className="main-content">
          <div className="left-panel">
            <AskForm onNewAnswer={handleNewAnswer} />
            <UploadPDF />
          </div>
          <div className="right-panel">
            <UsageDashboard />
          </div>
        </div>

        {renderAnswer()}
      </div>
    </div>
  );
}

export default App;
