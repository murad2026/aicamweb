import axios from 'axios';

const BASE_URL = ['https:', '', 'b48a-108-26-229-43.ngrok-free.app'].join('/');

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'ngrok-skip-browser-warning': 'true'
  }
});

api.interceptors.request.use(function(config) {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = 'Bearer ' + token;
  }
  return config;
});

export default api;
