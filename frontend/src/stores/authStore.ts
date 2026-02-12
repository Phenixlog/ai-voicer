import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserSettings } from '../types';
import { authApi } from '../api/auth';

interface AuthState {
  // State
  user: User | null;
  settings: UserSettings | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  fetchSettings: () => Promise<void>;
  updateSettings: (settings: Partial<UserSettings>) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      settings: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.login(email);
          const user = await authApi.getMe();
          const settings = await authApi.getSettings();
          set({ 
            user, 
            settings, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Login failed', 
            isLoading: false 
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authApi.logout();
        } catch {
          // Ignore logout errors
        }
        set({ 
          user: null, 
          settings: null, 
          isAuthenticated: false, 
          isLoading: false 
        });
      },

      fetchUser: async () => {
        if (!authApi.isAuthenticated()) return;
        try {
          const user = await authApi.getMe();
          set({ user, isAuthenticated: true });
        } catch {
          set({ user: null, isAuthenticated: false });
        }
      },

      fetchSettings: async () => {
        if (!authApi.isAuthenticated()) return;
        try {
          const settings = await authApi.getSettings();
          set({ settings });
        } catch {
          // Ignore settings fetch errors
        }
      },

      updateSettings: async (newSettings: Partial<UserSettings>) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.updateSettings(newSettings);
          const settings = await authApi.getSettings();
          set({ settings, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Update failed', 
            isLoading: false 
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'theoria-auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
