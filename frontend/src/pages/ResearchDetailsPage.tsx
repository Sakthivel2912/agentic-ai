/**
 * AI Council - Research Details Page
 * Display full details of a research session with real-time updates
 */
import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useResearchStore } from '../store/researchStore'
import { useSSE } from '../hooks/useSSE'
import { SessionStatus } from '../types/research'
import { Button } from '../components/Button'

export const ResearchDetailsPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentSession, loading, error, getSession, startSession, cancelSession, deleteSession, setCurrentSession } = useResearchStore()

  // SSE connection for real-time updates
  const { isConnected: sseConnected } = useSSE({
    sessionId: id || '',
    enabled: !!id && currentSession?.status === SessionStatus.RUNNING,
    onProgress: (data) => {
      console.log('Progress update:', data)
      if (currentSession) {
        setCurrentSession({
          ...currentSession,
          progress: data.progress,
          current_stage: data.current_stage,
        })
      }
    },
    onAgentOutput: (data) => {
      console.log('Agent output:', data)
      if (currentSession) {
        setCurrentSession({
          ...currentSession,
          agent_outputs: {
            ...currentSession.agent_outputs,
            [data.agent_id]: data.output,
          },
        })
      }
    },
    onError: (data) => {
      console.error('SSE error:', data)
      if (currentSession) {
        setCurrentSession({
          ...currentSession,
          error_message: data.error_message,
          status: SessionStatus.FAILED,
        })
      }
    },
    onCompletion: (data) => {
      console.log('Completion:', data)
      if (currentSession) {
        setCurrentSession({
          ...currentSession,
          final_answer: data.final_answer,
          status: SessionStatus.COMPLETED,
          progress: 100,
        })
      }
    },
    onKeepalive: () => {
      // Keepalive received, connection is alive
    },
  })

  useEffect(() => {
    if (id) {
      loadSession()
    }
  }, [id])

  const loadSession = () => {
    if (id) {
      getSession(id)
    }
  }

  const handleStart = async () => {
    if (id) {
      try {
        await startSession(id)
        loadSession()
      } catch (err) {
        console.error('Failed to start session:', err)
      }
    }
  }

  const handleCancel = async () => {
    if (id && window.confirm('Are you sure you want to cancel this session?')) {
      try {
        await cancelSession(id)
        loadSession()
      } catch (err) {
        console.error('Failed to cancel session:', err)
      }
    }
  }

  const handleDelete = async () => {
    if (id && window.confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSession(id)
        navigate('/research')
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

  if (loading && !currentSession) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading session...</p>
        </div>
      </div>
    )
  }

  if (!currentSession) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">Session not found</p>
          <Button variant="primary" onClick={() => navigate('/research')}>
            Back to Research
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{currentSession.title}</h1>
            <p className="text-gray-600 mt-2">{currentSession.question}</p>
            {currentSession.status === SessionStatus.RUNNING && (
              <div className="mt-2 flex items-center space-x-2">
                <span className={`inline-block w-2 h-2 rounded-full ${sseConnected ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
                <span className="text-sm text-gray-500">
                  {sseConnected ? 'Live connection' : 'Connecting...'}
                </span>
              </div>
            )}
          </div>
          <div className="flex space-x-2">
            {currentSession.status === SessionStatus.DRAFT && (
              <Button variant="primary" onClick={handleStart}>
                Start Research
              </Button>
            )}
            {currentSession.status === SessionStatus.RUNNING && (
              <Button variant="secondary" onClick={handleCancel}>
                Cancel
              </Button>
            )}
            <Button variant="secondary" onClick={() => navigate('/research')}>
              Back
            </Button>
            <Button variant="danger" onClick={handleDelete}>
              Delete
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Status and Progress */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm font-medium text-gray-500">Status</span>
            <div className="mt-1">
              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(currentSession.status)}`}>
                {currentSession.status}
              </span>
            </div>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-500">Current Stage</span>
            <div className="mt-1 text-sm text-gray-900">{currentSession.current_stage}</div>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-500">Progress</span>
            <div className="mt-1">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full"
                  style={{ width: `${currentSession.progress}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-900">{currentSession.progress.toFixed(0)}%</span>
            </div>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-500">Created</span>
            <div className="mt-1 text-sm text-gray-900">
              {new Date(currentSession.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Selected Agents */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Selected Agents</h2>
        {currentSession.selected_agents.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {currentSession.selected_agents.map((agentId) => (
              <span
                key={agentId}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {agentId}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No agents selected</p>
        )}
      </div>

      {/* Agent Outputs */}
      {Object.keys(currentSession.agent_outputs).length > 0 && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Agent Outputs</h2>
          <div className="space-y-4">
            {Object.entries(currentSession.agent_outputs).map(([agentId, output]) => (
              <div key={agentId} className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-medium text-gray-900">{agentId}</h3>
                <pre className="mt-2 text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded">
                  {JSON.stringify(output, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Final Answer */}
      {currentSession.final_answer && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Final Answer</h2>
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{currentSession.final_answer}</p>
          </div>
        </div>
      )}

      {/* Sources */}
      {currentSession.sources.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Sources</h2>
          <div className="space-y-3">
            {currentSession.sources.map((source, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded">
                <h3 className="font-medium text-gray-900">{source.title || `Source ${index + 1}`}</h3>
                {source.url && (
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    {source.url}
                  </a>
                )}
                {source.score && (
                  <span className="ml-2 text-xs text-gray-500">Score: {source.score.toFixed(2)}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Message */}
      {currentSession.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-red-900 mb-2">Error</h2>
          <p className="text-red-700">{currentSession.error_message}</p>
        </div>
      )}

      {/* Metadata */}
      {Object.keys(currentSession.metadata).length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Metadata</h2>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded">
            {JSON.stringify(currentSession.metadata, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
