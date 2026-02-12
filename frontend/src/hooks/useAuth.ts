import { useAuthStore } from '../stores/authStore';

export const useAuth = () => {
  const store = useAuthStore();
  
  return {
    user: store.user,
    settings: store.settings,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    logout: store.logout,
    fetchUser: store.fetchUser,
    fetchSettings: store.fetchSettings,
    updateSettings: store.updateSettings,
    clearError: store.clearError,
  };
};
