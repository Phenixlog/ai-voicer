import { apiClient } from './client';
import type { LoginRequest, TokenResponse, User, UserSettings } from '../types';

export const authApi = {
  async login(email: string): Promise<TokenResponse> {
    const data: LoginRequest = { email };
    const response = await apiClient.post<TokenResponse>('/v1/auth/login', data);
    
    // Store tokens
    apiClient.setToken(response.access_token);
    localStorage.setItem('theoria_refresh_token', response.refresh_token);
    
    return response;
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('theoria_refresh_token');
    if (refreshToken) {
      try {
        await apiClient.post('/v1/auth/logout', { refresh_token: refreshToken });
      } catch {
        // Ignore errors on logout
      }
    }
    apiClient.setToken(null);
  },

  async logoutAll(): Promise<void> {
    await apiClient.post('/v1/auth/logout-all', {});
    apiClient.setToken(null);
  },

  async getMe(): Promise<User> {
    return apiClient.get<User>('/v1/me');
  },

  async getSettings(): Promise<UserSettings> {
    return apiClient.get<UserSettings>('/v1/me/settings');
  },

  async updateSettings(settings: Partial<UserSettings>): Promise<void> {
    return apiClient.patch('/v1/me/settings', settings);
  },

  isAuthenticated(): boolean {
    return !!apiClient.getToken();
  },
};
