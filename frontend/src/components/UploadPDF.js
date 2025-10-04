import React, { useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function UploadPDF() {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadFile = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
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

  return (
    <div className="input-area">
      <input type="file" onChange={handleFileChange} />
      <button onClick={uploadFile} style={{ marginTop: "10px" }}>
        Upload PDF
      </button>
    </div>
  );
}

export default UploadPDF;
