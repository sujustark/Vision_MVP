import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1',
});

// Attach token automatically
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// REGISTER EVENT API
export const registerEvent = async (storagePath) => {
    const response = await api.post('/register', { storage_path: storagePath });
    return response.data;
};

// FACE MATCH API
export const matchFace = async (token, file, k = 5) => {
    const formData = new FormData();
    formData.append('token', token);
    formData.append('file', file);
    formData.append('k', k);

    const response = await api.post('/match', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export default api;
