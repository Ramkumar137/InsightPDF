import axios, { AxiosInstance } from 'axios';
import { auth } from '@/lib/firebase';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

console.log('🔗 API Base URL:', API_BASE_URL);

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for large file uploads
});

// Request interceptor to add Firebase token
api.interceptors.request.use(
  async (config) => {
    try {
      const user = auth.currentUser;
      
      if (user) {
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
        console.log('🔐 Added auth token to request');
      } else {
        console.warn('⚠️ No authenticated user found');
      }
    } catch (error) {
      console.error('❌ Error getting auth token:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('🔒 Unauthorized - Please log in again');
      // Optionally redirect to login
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      console.error('🚫 Forbidden - Access denied');
    } else if (error.response?.status >= 500) {
      console.error('💥 Server error - Please try again later');
    }
    
    return Promise.reject(error);
  }
);

export default api;