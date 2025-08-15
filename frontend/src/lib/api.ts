/**
 * API Client for Report Card Assistant Frontend
 * 
 * Docker-aware API client for session-based authentication with FastAPI backend.
 * Uses service names within Docker network for backend communication.
 */

// Types for API responses and errors
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: "form_teacher" | "year_head" | "admin";
  school_id: number;
  school_name: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  message: string;
}

export interface ApiErrorResponse {
  detail: string;
  type?: string;
  code?: string;
}

// Custom error classes
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

// API Client Configuration
class ApiClient {
  private readonly baseURL: string;

  constructor() {
    // Docker-aware API configuration
    // Server-side (within Docker network): http://backend:8000/api/v1  
    // Client-side (browser): http://localhost:8000/api/v1
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  }

  /**
   * Generic request method with error handling and Docker network support
   */
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      credentials: 'include', // Critical: include cookies for session authentication
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      // Handle authentication errors
      if (response.status === 401) {
        throw new AuthError('Authentication required');
      }

      if (response.status === 403) {
        throw new AuthError('Permission denied');
      }

      // Handle other HTTP errors
      if (!response.ok) {
        let errorMessage = 'Request failed';
        
        try {
          const errorData: ApiErrorResponse = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If we can't parse error JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        throw new ApiError(errorMessage, response.status);
      }

      // Parse successful response
      return await response.json();
    } catch (error) {
      // Handle network errors (Docker connectivity issues)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Backend service not available - check Docker network');
      }
      
      // Re-throw our custom errors
      if (error instanceof ApiError || error instanceof AuthError || error instanceof NetworkError) {
        throw error;
      }

      // Handle unexpected errors
      throw new Error(`Unexpected error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  // Convenience methods for common HTTP verbs
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // Authentication-specific methods
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return this.post<LoginResponse>('/auth/login', credentials);
  }

  async logout(): Promise<{ message: string }> {
    return this.post<{ message: string }>('/auth/logout');
  }

  async getCurrentUser(): Promise<User> {
    return this.get<User>('/auth/me');
  }

  async getAuthStatus(): Promise<{ authenticated: boolean; user?: User }> {
    return this.get<{ authenticated: boolean; user?: User }>('/auth/status');
  }

  // Health check for Docker network validation
  async healthCheck(): Promise<{ status: string }> {
    // Use base backend URL without /api/v1 prefix for health endpoint
    const healthUrl = this.baseURL.replace('/api/v1', '/health');
    const response = await fetch(healthUrl, { credentials: 'include' });
    
    if (!response.ok) {
      throw new NetworkError('Backend health check failed');
    }
    
    return response.json();
  }

  // Download blob (for PDF downloads)
  async downloadBlob(endpoint: string, data?: unknown): Promise<{ blob: Blob; filename?: string }> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      method: 'POST',
      credentials: 'include', // Critical: include cookies for session authentication
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    };

    try {
      const response = await fetch(url, config);

      // Handle authentication errors
      if (response.status === 401) {
        throw new AuthError('Authentication required');
      }

      if (response.status === 403) {
        throw new AuthError('Permission denied');
      }

      // Handle other HTTP errors
      if (!response.ok) {
        let errorMessage = 'Request failed';
        
        try {
          const errorData: ApiErrorResponse = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If we can't parse error JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        throw new ApiError(errorMessage, response.status);
      }

      // Get blob and filename
      const blob = await response.blob();
      
      // Extract filename from response headers
      const contentDisposition = response.headers.get('content-disposition');
      const filename = contentDisposition 
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : undefined;

      return { blob, filename };
    } catch (error) {
      // Handle network errors (Docker connectivity issues)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Backend service not available - check Docker network');
      }
      
      // Re-throw our custom errors
      if (error instanceof ApiError || error instanceof AuthError || error instanceof NetworkError) {
        throw error;
      }

      // Handle unexpected errors
      throw new Error(`Unexpected error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export convenience functions for common operations
export const auth = {
  login: (credentials: LoginRequest) => apiClient.login(credentials),
  logout: () => apiClient.logout(),
  getCurrentUser: () => apiClient.getCurrentUser(),
  getStatus: () => apiClient.getAuthStatus(),
};

export const api = {
  get: <T>(endpoint: string) => apiClient.get<T>(endpoint),
  post: <T>(endpoint: string, data?: unknown) => apiClient.post<T>(endpoint, data),
  put: <T>(endpoint: string, data?: unknown) => apiClient.put<T>(endpoint, data),
  delete: <T>(endpoint: string) => apiClient.delete<T>(endpoint),
  downloadBlob: (endpoint: string, data?: unknown) => apiClient.downloadBlob(endpoint, data),
  healthCheck: () => apiClient.healthCheck(),
};

export default apiClient;