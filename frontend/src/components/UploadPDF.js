import React, { useState } from 'react';

function UploadPDF() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMessage(data.message);
      setError('');
    } catch (error) {
      setError('Error uploading file.');
      console.error('There was an error!', error);
    }
  };

  return (
    <div className="input-area">
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".pdf" />
        <button type="submit">Upload</button>
      </form>
      {message && <p className="message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default UploadPDF;
