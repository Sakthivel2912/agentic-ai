/**
 * AI Council - Authentication API
 */
import apiClient from './client';
import type {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  User,
  ApiResponse
} from '../types';

const AUTH_BASE_URL = '/api/v1/auth';

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<ApiResponse<{ user: User }>> => {
    const response = await apiClient.post<ApiResponse<{ user: User }>>(
      `${AUTH_BASE_URL}/register`,
      data
    );
    return response.data;
  },

  /**
   * Login user
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      `${AUTH_BASE_URL}/login`,
      credentials
    );
    return response.data;
  },

  /**
   * Get current user
   */
  getCurrentUser: async (token: string): Promise<User> => {
    const response = await apiClient.get<User>(
      `${AUTH_BASE_URL}/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  /**
   * Update current user
   */
  updateCurrentUser: async (
    token: string,
    data: Partial<User>
  ): Promise<ApiResponse<{ user: User }>> => {
    const response = await apiClient.patch<ApiResponse<{ user: User }>>(
      `${AUTH_BASE_URL}/me`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  /**
   * Change password
   */
  changePassword: async (
    token: string,
    data: {
      current_password: string;
      new_password: string;
      confirm_password: string;
    }
  ): Promise<ApiResponse> => {
    const response = await apiClient.post<ApiResponse>(
      `${AUTH_BASE_URL}/change-password`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  /**
   * Logout
   */
  logout: async (token: string): Promise<ApiResponse> => {
    const response = await apiClient.post<ApiResponse>(
      `${AUTH_BASE_URL}/logout`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },
};
