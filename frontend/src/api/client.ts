const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8090';

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.loadToken();
  }

  private loadToken() {
    this.accessToken = localStorage.getItem('theoria_access_token');
  }

  setToken(token: string | null) {
    this.accessToken = token;
    if (token) {
      localStorage.setItem('theoria_access_token', token);
    } else {
      localStorage.removeItem('theoria_access_token');
      localStorage.removeItem('theoria_refresh_token');
    }
  }

  getToken(): string | null {
    return this.accessToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Token expired, try to refresh
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry request with new token
          headers['Authorization'] = `Bearer ${this.accessToken}`;
          const retryResponse = await fetch(url, { ...config, headers });
          return this.handleResponse<T>(retryResponse);
        }
        throw new ApiError('Session expired', 401);
      }

      return this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Network error', 0);
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let message = 'An error occurred';
      try {
        const data = await response.json();
        message = data.detail || data.message || message;
      } catch {
        message = response.statusText || message;
      }
      throw new ApiError(message, response.status);
    }

    // Handle empty responses
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('theoria_refresh_token');
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        this.setToken(null);
        return false;
      }

      const data = await response.json();
      this.setToken(data.access_token);
      localStorage.setItem('theoria_refresh_token', data.refresh_token);
      return true;
    } catch {
      this.setToken(null);
      return false;
    }
  }

  // HTTP methods
  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  post<T>(endpoint: string, body: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  patch<T>(endpoint: string, body: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
    });
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export class ApiError extends Error {
  status: number;
  
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
