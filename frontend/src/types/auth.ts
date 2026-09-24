/**
 * AI Council - Authentication Types
 */

export interface User {
  id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  role: string;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
  preferences: Record<string, any>;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  request_id?: string;
}
