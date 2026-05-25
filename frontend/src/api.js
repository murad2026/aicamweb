import axios from 'axios';

const BASE_URL = 'https://philadelphia-aqua-herself-portland.trycloudflare.com';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'ngrok-skip-browser-warning': 'true',
    'bypass-tunnel-reminder': 'true'
  }
});

api.interceptors.request.use(function(config) {
  const token = localStorage.getItem('token');
  if (token) { config.headers['Authorization'] = 'Bearer ' + token; }
  return config;
});

export default api;
