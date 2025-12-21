import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config
  },
  (error) => Promise.reject(error)
);

export const registerEvent = async (token, file) => {
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

export default api;