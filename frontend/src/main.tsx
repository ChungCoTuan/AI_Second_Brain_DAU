import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const originalFetch = window.fetch;
window.fetch = async (...args) => {
  let [resource, config] = args;
  
  if (!config) {
    config = {};
  }
  
  if (!config.headers) {
    config.headers = {};
  }
  
  const token = localStorage.getItem('token');
  if (token) {
    if (config.headers instanceof Headers) {
      config.headers.set('Authorization', `Bearer ${token}`);
    } else {
      (config.headers as any)['Authorization'] = `Bearer ${token}`;
    }
  }
  
  const response = await originalFetch(resource, config);
  
  // Handle 401 globally
  if (response.status === 401 && window.location.pathname !== '/login') {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
  
  return response;
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
