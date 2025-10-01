import { useState } from "react";
import { uploadPDF } from "../api";

export default function UploadPDF() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    try {
      const res = await uploadPDF(file);
      setResponse(res);
    } catch (err) {
      console.error(err);
      setResponse({ filename: file.name, location: "Upload failed" });
    }
  };

  return (
    <div>
      <h2>Upload PDF</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" style={{ marginLeft: "10px" }}>Upload</button>
      </form>
      {response && (
        <div style={{ marginTop: "20px" }}>
          <p><strong>Filename:</strong> {response.filename}</p>
          <p><strong>Location:</strong> {response.location}</p>
        </div>
      )}
    </div>
  );
}
