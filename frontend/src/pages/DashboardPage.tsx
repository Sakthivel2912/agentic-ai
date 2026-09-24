/**
 * AI Council - Dashboard Page
 */
import React from 'react';

export const DashboardPage: React.FC = () => {
  const stats = [
    { label: 'Sessions', value: '24', color: 'bg-blue-500' },
    { label: 'Running', value: '3', color: 'bg-green-500' },
    { label: 'Reports', value: '18', color: 'bg-purple-500' },
    { label: 'Documents', value: '12', color: 'bg-orange-500' },
  ];

  const recentResearch = [
    { id: 1, title: 'Microservices Architecture Analysis', status: 'Completed', date: '2024-01-15' },
    { id: 2, title: 'AI Model Evaluation', status: 'Running', date: '2024-01-14' },
    { id: 3, title: 'Cost Optimization Strategy', status: 'Completed', date: '2024-01-13' },
  ];

  const systemHealth = {
    database: 'Connected',
    llm: 'Online',
    uptime: '99.9%',
  };

  return (
    <div className="page-enter">
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-[#e2775f]">Council overview</p>
          <h1 className="text-4xl font-black tracking-tight text-[#123c52]">Good morning, strategist.</h1>
          <p className="mt-2 text-[#557083]">A quick read on the questions your council is working through.</p>
        </div>
        <div className="rounded-2xl bg-[#123c52] px-4 py-3 text-right text-white shadow-lg shadow-[#123c52]/15">
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#8debd7]">Today</p>
          <p className="font-bold">Research mode: active</p>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="glass-panel rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-[#557083]">{stat.label}</p>
                <p className="mt-1 text-3xl font-black text-[#123c52]">{stat.value}</p>
              </div>
              <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${stat.color} shadow-lg`}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Two Column Layout */}
      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Research */}
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="mb-4 text-lg font-black text-[#123c52]">Recent Research</h2>
          <div className="space-y-3">
            {recentResearch.map((research) => (
              <div key={research.id} className="flex items-center justify-between rounded-xl border border-[#e5eef0] bg-white/70 p-3">
                <div>
                  <p className="font-bold text-[#27475b]">{research.title}</p>
                  <p className="text-sm text-[#78909d]">{research.date}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded ${
                  research.status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {research.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="mb-4 text-lg font-black text-[#123c52]">System Health</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[#557083]">Database</span>
              <span className="flex items-center text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                {systemHealth.database}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#557083]">LLM Service</span>
              <span className="flex items-center text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                {systemHealth.llm}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#557083]">System Uptime</span>
              <span className="font-bold text-[#123c52]">{systemHealth.uptime}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Research Activity / Agent Analytics */}
      <div className="glass-panel rounded-2xl p-6">
        <h2 className="mb-4 text-lg font-black text-[#123c52]">Research Activity / Agent Analytics</h2>
        <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-[#b9ddd5] bg-[#e8faf5]/70">
          <p className="font-medium text-[#557083]">Charts and analytics will be displayed here</p>
        </div>
      </div>
    </div>
  );
};
