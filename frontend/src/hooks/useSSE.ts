/**
 * AI Council - SSE Hook
 * Custom hook for Server-Sent Events (SSE) connections
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuthStore } from '../store/authStore'

interface UseSSEOptions {
  sessionId: string
  onProgress?: (data: any) => void
  onAgentOutput?: (data: any) => void
  onError?: (data: any) => void
  onCompletion?: (data: any) => void
  onKeepalive?: () => void
  enabled?: boolean
}

export const useSSE = ({
  sessionId,
  onProgress,
  onAgentOutput,
  onError,
  onCompletion,
  onKeepalive,
  enabled = true,
}: UseSSEOptions) => {
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const { token } = useAuthStore()

  const connect = useCallback(() => {
    if (!enabled || !sessionId || !token) {
      return
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const url = `${API_URL}/api/v1/events/sessions/${sessionId}/stream`

    try {
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        setIsConnected(true)
        setError(null)
        console.log('SSE connection opened')
      }

      eventSource.onerror = (e) => {
        setIsConnected(false)
        setError('SSE connection error')
        console.error('SSE error:', e)
      }

      eventSource.addEventListener('progress', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data)
          onProgress?.(data)
        } catch (err) {
          console.error('Error parsing progress event:', err)
        }
      })

      eventSource.addEventListener('agent_output', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data)
          onAgentOutput?.(data)
        } catch (err) {
          console.error('Error parsing agent_output event:', err)
        }
      })

      eventSource.addEventListener('error', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data)
          onError?.(data)
        } catch (err) {
          console.error('Error parsing error event:', err)
        }
      })

      eventSource.addEventListener('completion', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data)
          onCompletion?.(data)
        } catch (err) {
          console.error('Error parsing completion event:', err)
        }
      })

      eventSource.addEventListener('keepalive', (e: MessageEvent) => {
        try {
          JSON.parse(e.data)
          onKeepalive?.()
        } catch (err) {
          console.error('Error parsing keepalive event:', err)
        }
      })
    } catch (err) {
      setError('Failed to create SSE connection')
      console.error('Failed to create SSE connection:', err)
    }
  }, [sessionId, token, enabled, onProgress, onAgentOutput, onError, onCompletion, onKeepalive])

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsConnected(false)
      console.log('SSE connection closed')
    }
  }, [])

  useEffect(() => {
    if (enabled && sessionId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, sessionId, connect, disconnect])

  return {
    isConnected,
    error,
    connect,
    disconnect,
  }
}
