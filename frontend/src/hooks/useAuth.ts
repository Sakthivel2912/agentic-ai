/**
 * AI Council - Authentication Hook
 */
import { useAuthStore } from '../store/authStore';
import { authApi } from '../api/auth.api';
import { useCallback } from 'react';

export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    setAuth,
    setUser,
    logout,
    setLoading,
    setError,
    clearError,
  } = useAuthStore();

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    clearError();
    try {
      const response = await authApi.login({ email, password });
      setAuth(response);
      return true;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, setAuth, setError]);

  const register = useCallback(async (data: {
    full_name: string;
    email: string;
    password: string;
    confirm_password: string;
  }) => {
    setLoading(true);
    clearError();
    try {
      await authApi.register(data);
      return true;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, setError]);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const userData = await authApi.getCurrentUser(token);
      setUser(userData);
    } catch (error) {
      // If token is invalid, logout
      logout();
    } finally {
      setLoading(false);
    }
  }, [token, setLoading, setUser, logout]);

  const updateProfile = useCallback(async (data: Partial<{
    full_name: string;
    email: string;
    preferences: Record<string, any>;
  }>) => {
    if (!token) return false;
    
    setLoading(true);
    clearError();
    try {
      const response = await authApi.updateCurrentUser(token, data);
      if (response.data?.user) {
        setUser(response.data.user);
      }
      return true;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Update failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [token, setLoading, clearError, setUser, setError]);

  const changePassword = useCallback(async (data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) => {
    if (!token) return false;
    
    setLoading(true);
    clearError();
    try {
      await authApi.changePassword(token, data);
      return true;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Password change failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [token, setLoading, clearError, setError]);

  const handleLogout = useCallback(async () => {
    if (token) {
      try {
        await authApi.logout(token);
      } catch (error) {
        // Continue with logout even if API call fails
        console.error('Logout API call failed:', error);
      }
    }
    logout();
  }, [token, logout]);

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    refreshUser,
    updateProfile,
    changePassword,
    logout: handleLogout,
    clearError,
  };
};
