/**
 * AI Council - Login Page
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { authApi } from '../api/auth.api';
import type { LoginCredentials } from '../types';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAuth, setLoading, setError, isLoading, error } = useAuthStore();
  const [credentials, setCredentials] = useState<LoginCredentials>({ email: '', password: '' });

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await authApi.login(credentials);
      setAuth(response);
      navigate('/dashboard');
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="workspace-grid relative flex min-h-screen items-center justify-center overflow-hidden bg-[#f4f7fb] px-4 py-10">
      <div className="pointer-events-none absolute -left-24 -top-24 h-72 w-72 rounded-full bg-[#8debd7]/40 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -right-16 h-96 w-96 rounded-full bg-[#ffad98]/35 blur-3xl" />
      <div className="page-enter relative w-full max-w-md">
        <div className="glass-panel rounded-[2rem] p-8 sm:p-10">
          <div className="mb-8">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#123c52] text-lg font-black text-[#8debd7]">AI</div>
              <div>
                <p className="text-lg font-black tracking-tight text-[#123c52]">AI Council</p>
                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#e2775f]">Decision studio</p>
              </div>
            </div>
            <p className="mb-2 text-sm font-bold uppercase tracking-[0.18em] text-[#e2775f]">Welcome back</p>
            <h1 className="text-3xl font-black tracking-tight text-[#123c52]">Bring your hardest question.</h1>
            <p className="mt-2 text-[#557083]">Sign in to convene your AI research council.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="mb-2 block text-sm font-bold text-[#315469]">Email</label>
              <input id="email" name="email" type="email" required value={credentials.email}
                onChange={(event) => setCredentials({ ...credentials, email: event.target.value })}
                className="w-full rounded-xl border border-[#d7e3e8] bg-white/75 px-4 py-3 text-[#172033] outline-none transition placeholder:text-[#9aadb6] focus:border-[#42cdb3] focus:ring-4 focus:ring-[#42cdb3]/15"
                placeholder="you@example.com" />
            </div>
            <div>
              <label htmlFor="password" className="mb-2 block text-sm font-bold text-[#315469]">Password</label>
              <input id="password" name="password" type="password" required value={credentials.password}
                onChange={(event) => setCredentials({ ...credentials, password: event.target.value })}
                className="w-full rounded-xl border border-[#d7e3e8] bg-white/75 px-4 py-3 text-[#172033] outline-none transition placeholder:text-[#9aadb6] focus:border-[#42cdb3] focus:ring-4 focus:ring-[#42cdb3]/15"
                placeholder="Enter your password" />
            </div>

            {error && <div className="rounded-xl border border-[#f4b4a7] bg-[#fff0ed] px-4 py-3 text-sm font-medium text-[#a74838]">{error}</div>}

            <button type="submit" disabled={isLoading}
              className="w-full rounded-xl bg-[#123c52] px-4 py-3 font-bold text-white shadow-lg shadow-[#123c52]/20 transition hover:-translate-y-0.5 hover:bg-[#1b536c] focus:outline-none focus:ring-4 focus:ring-[#42cdb3]/30 disabled:cursor-not-allowed disabled:opacity-50">
              {isLoading ? 'Signing in...' : 'Sign in to council'}
            </button>
          </form>

          <p className="mt-7 text-center text-sm text-[#557083]">
            Do not have an account?{' '}
            <a href="/register" className="font-bold text-[#167d70] hover:text-[#e2775f]">Create one</a>
          </p>
        </div>
      </div>
    </div>
  );
};
