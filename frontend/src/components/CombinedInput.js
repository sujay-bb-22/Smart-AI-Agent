import React, { useState } from 'react';
import AskForm from './AskForm';
import UploadPDF from './UploadPDF';
import './CombinedInput.css';

function CombinedInput({ onNewAnswer }) {
  const [activeTab, setActiveTab] = useState('ask'); // 'ask' or 'upload'

  return (
    <div className="combined-input-container">
      <div className="tab-selector">
        <button
          className={activeTab === 'ask' ? 'active' : ''}
          onClick={() => setActiveTab('ask')}
        >
          Ask a Question
        </button>
        <button
          className={activeTab === 'upload' ? 'active' : ''}
          onClick={() => setActiveTab('upload')}
        >
          Upload PDF
        </button>
      </div>
      <div className="tab-content">
        {activeTab === 'ask' && <AskForm onNewAnswer={onNewAnswer} />}
        {activeTab === 'upload' && <UploadPDF />}
      </div>
    </div>
  );
}

export default CombinedInput;
