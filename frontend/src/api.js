import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const registerEvent = async (storagePath) => {
  const response = await axios.post(`${API_URL}/studio/register`, { storage_path: storagePath });
  return response.data;
};

export const matchFace = async (token, file) => {
  const formData = new FormData();
  formData.append('token', token);
  formData.append('file', file);
  formData.append('k', 5);

  const response = await axios.post(`${API_URL}/match`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
