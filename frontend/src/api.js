import axios from 'axios';

const BASE_URL = 'https://api.aianycamera.com';

const api = axios.create({
  baseURL: BASE_URL,
});

api.interceptors.request.use(function(config) {
  const token = localStorage.getItem('token');
  if (token) { config.headers['Authorization'] = 'Bearer ' + token; }
  return config;
});

export default api;
