/**
 * AI Council - Research History Page
 * List all research sessions for the authenticated user
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useResearchStore } from '../store/researchStore'
import { SessionStatus } from '../types/research'
import { Button } from '../components/Button'

export const ResearchHistoryPage = () => {
  const navigate = useNavigate()
  const { sessions, loading, error, listSessions, deleteSession, total_pages } = useResearchStore()
  const [currentPage, setCurrentPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    loadSessions()
  }, [currentPage, statusFilter])

  const loadSessions = () => {
    listSessions({
      page: currentPage,
      status: statusFilter || undefined,
    })
  }

  const handleDelete = async (sessionId: string) => {
    if (window.confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSession(sessionId)
        loadSessions()
      } catch (err) {
        console.error('Failed to delete session:', err)
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case SessionStatus.COMPLETED:
        return 'bg-green-100 text-green-800'
      case SessionStatus.RUNNING:
        return 'bg-blue-100 text-blue-800'
      case SessionStatus.FAILED:
        return 'bg-red-100 text-red-800'
      case SessionStatus.CANCELLED:
        return 'bg-gray-100 text-gray-800'
      case SessionStatus.QUEUED:
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= total_pages) {
      setCurrentPage(newPage)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Research History</h1>
          <p className="text-gray-600 mt-2">View and manage your research sessions</p>
        </div>
        <Button variant="primary" onClick={() => navigate('/research/new')}>
          New Research
        </Button>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center space-x-4">
        <div>
          <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
            Status Filter
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setCurrentPage(1)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value={SessionStatus.DRAFT}>Draft</option>
            <option value={SessionStatus.QUEUED}>Queued</option>
            <option value={SessionStatus.RUNNING}>Running</option>
            <option value={SessionStatus.COMPLETED}>Completed</option>
            <option value={SessionStatus.FAILED}>Failed</option>
            <option value={SessionStatus.CANCELLED}>Cancelled</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading sessions...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No research sessions found</p>
          <Button variant="primary" onClick={() => navigate('/research/new')}>
            Create Your First Session
          </Button>
        </div>
      ) : (
        <>
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sessions.map((session) => (
                  <tr key={session.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{session.title}</div>
                      <div className="text-sm text-gray-500 truncate max-w-xs">{session.question}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(session.status)}`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full"
                          style={{ width: `${session.progress}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{session.progress.toFixed(0)}%</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => navigate(`/research/${session.id}`)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDelete(session.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {total_pages > 1 && (
            <div className="mt-6 flex justify-center items-center space-x-2">
              <Button
                variant="secondary"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {currentPage} of {total_pages}
              </span>
              <Button
                variant="secondary"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === total_pages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
