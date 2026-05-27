import axios from 'axios';

const backendTarget = import.meta.env.VITE_BACKEND_TARGET;
const baseURL = backendTarget
  ? (backendTarget.endsWith('/api') ? backendTarget : `${backendTarget.replace(/\/$/, '')}/api`)
  : '/api';

const api = axios.create({
  baseURL: baseURL,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('heartguard_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      localStorage.removeItem('heartguard_token');
      localStorage.removeItem('heartguard_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
