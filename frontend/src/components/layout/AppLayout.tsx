/**
 * AI Council - Main Application Layout
 */
import React from 'react';
import { useNavigate, Link, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/research/new', label: 'New Research' },
    { path: '/research', label: 'History' },
    { path: '/agent-monitor', label: 'Agent Monitor' },
    { path: '/knowledge', label: 'Knowledge' },
    { path: '/reports', label: 'Reports' },
    { path: '/evaluations', label: 'Evaluations' },
    { path: '/settings', label: 'Settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-[#f4f7fb] text-[#172033]">
      <div className="flex flex-col h-screen">
        {/* Top Header Bar */}
        <header className="relative z-10 flex items-center justify-between border-b border-[#dce7ed] bg-white/85 px-6 py-4 backdrop-blur-xl">
          <div className="flex items-center space-x-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#123c52] text-sm font-black text-[#8debd7] shadow-lg shadow-[#123c52]/20">AI</div>
            <div>
              <h1 className="text-lg font-black tracking-tight text-[#123c52]">AI Council</h1>
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#e2775f]">Decision studio</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search..."
                className="w-64 rounded-xl border border-[#d7e3e8] bg-[#f7fafb] px-4 py-2 text-sm text-[#172033] outline-none transition focus:border-[#42cdb3] focus:ring-4 focus:ring-[#42cdb3]/15"
              />
            </div>
            {/* Notifications */}
            <button aria-label="Notifications" className="rounded-xl p-2 text-[#557083] transition hover:bg-[#e8faf5] hover:text-[#123c52]">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 overflow-y-auto bg-[#123c52] text-white">
            <div className="px-6 pb-3 pt-7 text-xs font-bold uppercase tracking-[0.2em] text-[#83dcca]">Workspace</div>
            <nav className="space-y-1 px-3">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`group block rounded-xl px-4 py-3 text-sm font-semibold transition-all ${
                    isActive(item.path)
                      ? 'bg-[#8debd7] text-[#123c52] shadow-lg shadow-black/10'
                      : 'text-[#d5e7e8] hover:bg-white/10 hover:text-white'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
              
              <div className="mt-5 border-t border-white/15 pt-5">
                <Link
                  to="/profile"
                  className="block rounded-xl px-4 py-3 text-sm font-semibold text-[#d5e7e8] transition hover:bg-white/10 hover:text-white"
                >
                  User Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full rounded-xl px-4 py-3 text-left text-[#ffad98] transition hover:bg-[#e2775f]/20 hover:text-white"
                >
                  Logout
                </button>
              </div>
            </nav>
          </aside>

          {/* Main content area */}
          <main className="workspace-grid flex-1 overflow-y-auto p-6 lg:p-9">
            <div className="page-enter mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};
