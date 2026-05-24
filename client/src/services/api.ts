import axios from 'axios';
import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  AnalyzeTextRequest,
  AnalyzeLinkRequest,
  AnalyzeFileRequest,
  AnalysisJob,
  AnalyticsSummary,
  UserAnalyticsSummary
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getErrorMessage = (error: any): string => {
  const detail = error?.response?.data?.detail;
  if (!detail) {
    return error?.message || 'An unexpected error occurred';
  }

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item.loc && item.msg) return `${item.loc.join('.')}: ${item.msg}`;
        return JSON.stringify(item);
      })
      .join(' | ');
  }

  if (typeof detail === 'object') {
    return JSON.stringify(detail);
  }

  return String(detail);
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const params = new URLSearchParams();
    params.append('username', data.email);
    params.append('password', data.password);

    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
};

export const analysisAPI = {
  analyzeText: async (data: AnalyzeTextRequest): Promise<AnalysisJob> => {
    const response = await api.post('/analyze/text', data);
    return response.data;
  },

  analyzeLink: async (data: AnalyzeLinkRequest): Promise<AnalysisJob> => {
    const response = await api.post('/analyze/link', data);
    return response.data;
  },

  analyzeFile: async (data: AnalyzeFileRequest): Promise<AnalysisJob> => {
    const formData = new FormData();
    formData.append('file', data.file);

    const response = await api.post('/analyze/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  checkExistingAnalysis: async (jobId: string): Promise<any> => {
    const response = await api.get(`/analyze/check-existing/${jobId}`);
    return response.data;
  },

  refreshAnalysis: async (jobId: string): Promise<AnalysisJob> => {
    const response = await api.post(`/analyze/refresh/${jobId}`);
    return response.data;
  },
};

export const historyAPI = {
  getHistory: async (): Promise<AnalysisJob[]> => {
    const response = await api.get('/history');
    return response.data;
  },

  getJobById: async (id: string): Promise<AnalysisJob> => {
    const response = await api.get(`/history/${id}`);
    return response.data;
  },

  deleteAll: async (): Promise<{ message: string }> => {
    const response = await api.delete('/history/');
    return response.data;
  },
};

export const analyticsAPI = {
  getSummary: async (): Promise<UserAnalyticsSummary> => {
    const response = await api.get('/analytics/summary');
    return response.data;
  },

  getJobAnalytics: async (jobId: string): Promise<AnalyticsSummary> => {
    const response = await api.get(`/analytics/job/${jobId}`);
    return response.data;
  },
};

export default api;