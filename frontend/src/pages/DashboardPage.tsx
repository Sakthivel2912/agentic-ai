/**
 * AI Council - Dashboard Page
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'
import { researchApi } from '../api/research.api'
import { ResearchSession, SessionStatus } from '../types/research'

interface DashboardData {
  totalSessions: number
  runningSessions: number
  totalReports: number
  totalDocuments: number
  recentSessions: ResearchSession[]
  databaseStatus: string
  llmConfigured: boolean
  refreshedAt: string
}

const sessionStatusStyles: Record<string, string> = {
  [SessionStatus.COMPLETED]: 'bg-green-100 text-green-800',
  [SessionStatus.RUNNING]: 'bg-yellow-100 text-yellow-800',
  [SessionStatus.FAILED]: 'bg-red-100 text-red-800',
  [SessionStatus.CANCELLED]: 'bg-gray-100 text-gray-700',
  [SessionStatus.QUEUED]: 'bg-blue-100 text-blue-800',
  [SessionStatus.DRAFT]: 'bg-gray-100 text-gray-700',
}

const statusBarColors: Record<string, string> = {
  [SessionStatus.COMPLETED]: 'bg-green-500',
  [SessionStatus.RUNNING]: 'bg-yellow-500',
  [SessionStatus.FAILED]: 'bg-red-500',
  [SessionStatus.CANCELLED]: 'bg-gray-400',
  [SessionStatus.QUEUED]: 'bg-blue-500',
  [SessionStatus.DRAFT]: 'bg-gray-400',
}

export const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const loadDashboard = async () => {
      setIsRefreshing(true)
      try {
        const [sessions, running, reports, documents, health] = await Promise.all([
          researchApi.listSessions({ page: 1, page_size: 5 }),
          researchApi.listSessions({ status: SessionStatus.RUNNING, page: 1, page_size: 1 }),
          apiClient.get('/api/v1/reports/', { params: { page: 1, page_size: 1 } }),
          apiClient.get('/api/v1/documents/', { params: { page: 1, page_size: 1 } }),
          apiClient.get('/health'),
        ])

        if (!active) return

        setDashboardData({
          totalSessions: sessions.total,
          runningSessions: running.total,
          totalReports: reports.data.data.total,
          totalDocuments: documents.data.data.total,
          recentSessions: sessions.sessions,
          databaseStatus: health.data.database,
          llmConfigured: health.data.llm_configured,
          refreshedAt: new Date().toISOString(),
        })
        setError(null)
      } catch (requestError: any) {
        if (!active) return
        setError(
          requestError.response?.data?.detail ||
          'Dashboard data could not be loaded. Check the API connection and try again.'
        )
      } finally {
        if (active) {
          setIsLoading(false)
          setIsRefreshing(false)
        }
      }
    }

    void loadDashboard()
    return () => {
      active = false
    }
  }, [refreshKey])

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setRefreshKey((current) => current + 1)
    }, 30_000)
    return () => window.clearInterval(intervalId)
  }, [])

  const stats = [
    { label: 'Sessions', value: dashboardData?.totalSessions, color: 'bg-blue-500' },
    { label: 'Running', value: dashboardData?.runningSessions, color: 'bg-green-500' },
    { label: 'Reports', value: dashboardData?.totalReports, color: 'bg-purple-500' },
    { label: 'Documents', value: dashboardData?.totalDocuments, color: 'bg-orange-500' },
  ]

  const statusCounts = (dashboardData?.recentSessions ?? []).reduce<Record<string, number>>(
    (counts, session) => {
      counts[session.status] = (counts[session.status] ?? 0) + 1
      return counts
    },
    {}
  )
  const recentSessionCount = dashboardData?.recentSessions.length ?? 0

  return (
    <div className="page-enter">
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-[#e2775f]">Council overview</p>
          <h1 className="text-4xl font-black tracking-tight text-[#123c52]">Good morning, strategist.</h1>
          <p className="mt-2 text-[#557083]">A quick read on the questions your council is working through.</p>
        </div>
        <div className="rounded-2xl bg-[#123c52] px-4 py-3 text-right text-white shadow-lg shadow-[#123c52]/15">
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#8debd7]">Workspace data</p>
          <p className="font-bold">
            {dashboardData
              ? `Updated ${new Date(dashboardData.refreshedAt).toLocaleTimeString()}`
              : isLoading ? 'Loading current data' : 'Data unavailable'}
          </p>
        </div>
      </div>

      {error && (
        <div role="alert" className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <span>
            {dashboardData ? 'Could not refresh dashboard data. Showing the last successful results.' : error}
          </span>
          <button
            type="button"
            onClick={() => setRefreshKey((current) => current + 1)}
            className="font-bold underline underline-offset-2"
          >
            Retry
          </button>
        </div>
      )}

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="glass-panel rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-[#557083]">{stat.label}</p>
                <p className="mt-1 text-3xl font-black text-[#123c52]" aria-live="polite">
                  {stat.value ?? (isLoading ? '...' : '—')}
                </p>
              </div>
              <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${stat.color} shadow-lg`}>
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="mb-4 text-lg font-black text-[#123c52]">Recent Research</h2>
          {isLoading && !dashboardData ? (
            <p className="py-8 text-center text-sm text-[#557083]">Loading research sessions...</p>
          ) : dashboardData?.recentSessions.length ? (
            <div className="space-y-3">
              {dashboardData.recentSessions.map((session) => (
                <Link
                  key={session.id}
                  to={`/research/${session.id}`}
                  className="flex items-center justify-between gap-3 rounded-xl border border-[#e5eef0] bg-white/70 p-3 transition hover:border-[#42cdb3]"
                >
                  <div className="min-w-0">
                    <p className="truncate font-bold text-[#27475b]">{session.title}</p>
                    <p className="text-sm text-[#78909d]">
                      {session.created_at
                        ? new Date(session.created_at).toLocaleDateString()
                        : 'Date unavailable'}
                    </p>
                  </div>
                  <span className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${sessionStatusStyles[session.status] ?? 'bg-gray-100 text-gray-700'}`}>
                    {session.status}
                  </span>
                </Link>
              ))}
            </div>
          ) : (
            <p className="py-8 text-center text-sm text-[#557083]">No research sessions yet.</p>
          )}
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <h2 className="mb-4 text-lg font-black text-[#123c52]">System Health</h2>
          <div className="space-y-4">
            {[
              { label: 'API', value: dashboardData ? 'Reachable' : isLoading ? 'Checking' : 'Unavailable', healthy: Boolean(dashboardData) },
              { label: 'Database', value: dashboardData?.databaseStatus ?? (isLoading ? 'Checking' : 'Unavailable'), healthy: dashboardData?.databaseStatus === 'connected' },
              { label: 'Groq API key', value: dashboardData ? dashboardData.llmConfigured ? 'Configured' : 'Missing' : isLoading ? 'Checking' : 'Unavailable', healthy: dashboardData?.llmConfigured ?? false },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <span className="text-[#557083]">{item.label}</span>
                <span className={`flex items-center ${item.healthy ? 'text-green-600' : 'text-[#78909d]'}`}>
                  <span className={`mr-2 h-2 w-2 rounded-full ${item.healthy ? 'bg-green-500' : 'bg-gray-400'}`} />
                  {item.value}
                </span>
              </div>
            ))}
          </div>
          {isRefreshing && dashboardData && (
            <p className="mt-5 text-right text-xs text-[#78909d]">Refreshing...</p>
          )}
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-6">
        <h2 className="mb-4 text-lg font-black text-[#123c52]">Recent Session Status</h2>
        {recentSessionCount ? (
          <div className="space-y-4">
            {Object.entries(statusCounts).map(([status, count]) => (
              <div key={status} className="grid grid-cols-[110px_1fr_32px] items-center gap-3 text-sm">
                <span className="capitalize text-[#557083]">{status.replace(/_/g, ' ')}</span>
                <div className="h-2 overflow-hidden rounded-full bg-[#e5eef0]">
                  <div
                    className={`h-full rounded-full ${statusBarColors[status] ?? 'bg-gray-400'}`}
                    style={{ width: `${(count / recentSessionCount) * 100}%` }}
                  />
                </div>
                <span className="text-right font-bold text-[#123c52]">{count}</span>
              </div>
            ))}
            <p className="pt-1 text-xs text-[#78909d]">Based on the latest {recentSessionCount} sessions.</p>
          </div>
        ) : (
          <p className="py-8 text-center text-sm text-[#557083]">No session activity to summarize.</p>
        )}
      </div>
    </div>
  )
}