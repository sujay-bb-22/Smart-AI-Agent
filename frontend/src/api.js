import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000"; // replace with deployed backend URL later

export const askQuestion = async (question) => {
  const res = await axios.post(`${BASE_URL}/ask/`, { question });
  return res.data;
};

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${BASE_URL}/upload_pdf/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const getUsage = async () => {
  const res = await axios.get(`${BASE_URL}/usage/`);
  return res.data;
};
