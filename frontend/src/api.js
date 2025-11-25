import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const registerEvent = async (storagePath) => {
  const response = await api.post('/studio/register', { storage_path: storagePath });
  return response.data;
};

export const matchFace = async (token, file) => {
  const formData = new FormData();
  formData.append('token', token);
  formData.append('file', file);
  formData.append('k', 5);

  const response = await api.post('/match', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
