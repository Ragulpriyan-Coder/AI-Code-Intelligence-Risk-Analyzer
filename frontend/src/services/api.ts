/**
 * API service for communicating with the backend.
 */
import axios, { AxiosError, AxiosInstance } from 'axios';

// Types
export interface User {
  id: number;
  email: string;
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SignupRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AnalyzeRequest {
  repo_url: string;
  branch?: string;
}

export interface AnalysisScores {
  security_score: number;
  maintainability_score: number;
  architecture_score: number;
  tech_debt_index: number;
  refactor_urgency: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface AnalysisResult {
  id: number;
  repo_name: string;
  repo_url: string;
  branch: string;
  metrics: Record<string, unknown>;
  scores: AnalysisScores;
  llm_explanation: string;
  files_analyzed: number;
  total_lines: number;
  analysis_duration_seconds: number;
}

export interface AnalysisListItem {
  id: number;
  repo_name: string;
  repo_url: string | null;
  security_score: number;
  maintainability_score: number;
  architecture_score: number;
  refactor_urgency: string;
  created_at: string;
}

// API Error type
export interface ApiError {
  detail: string;
}

// Token storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth functions
export const authService = {
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/signup', data);
    const { access_token, user } = response.data;
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    const { access_token, user } = response.data;
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    return response.data;
  },

  logout: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem(USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
  },

  verifyToken: async (): Promise<boolean> => {
    try {
      await api.post('/auth/verify');
      return true;
    } catch {
      return false;
    }
  },
};

// Analysis functions
export const analysisService = {
  analyzeRepo: async (data: AnalyzeRequest): Promise<AnalysisResult> => {
    const response = await api.post<AnalysisResult>('/analyze', data);
    return response.data;
  },

  getAnalysis: async (id: number): Promise<AnalysisResult> => {
    const response = await api.get<AnalysisResult>(`/analyze/${id}`);
    return response.data;
  },

  listAnalyses: async (limit = 20, offset = 0): Promise<AnalysisListItem[]> => {
    const response = await api.get<AnalysisListItem[]>('/analyze', {
      params: { limit, offset },
    });
    return response.data;
  },

  deleteAnalysis: async (id: number): Promise<void> => {
    await api.delete(`/analyze/${id}`);
  },
};

// Report functions
export const reportService = {
  downloadPdf: async (analysisId: number): Promise<Blob> => {
    const response = await api.get(`/reports/${analysisId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  downloadPdfWithFilename: async (analysisId: number, repoName: string): Promise<void> => {
    const blob = await reportService.downloadPdf(analysisId);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis-${repoName}-${analysisId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  getSummary: async (analysisId: number): Promise<Record<string, unknown>> => {
    const response = await api.get(`/reports/${analysisId}/summary`);
    return response.data;
  },
};

// Health check
export const healthService = {
  check: async (): Promise<Record<string, unknown>> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
