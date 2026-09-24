/**
 * AI Council - Research Session API Client
 */
import apiClient from './client'
import {
  ResearchSession,
  ResearchSessionCreate,
  ResearchSessionUpdate,
  ResearchSessionListResponse,
} from '../types/research'

export const researchApi = {
  /**
   * Create a new research session
   */
  createSession: async (data: ResearchSessionCreate): Promise<ResearchSession> => {
    const response = await apiClient.post('/api/v1/research/sessions', data)
    return response.data.data.session
  },

  /**
   * Get a research session by ID
   */
  getSession: async (sessionId: string): Promise<ResearchSession> => {
    const response = await apiClient.get(`/api/v1/research/sessions/${sessionId}`)
    return response.data.data.session
  },

  /**
   * List research sessions for the authenticated user
   */
  listSessions: async (params?: {
    status?: string
    category?: string
    page?: number
    page_size?: number
  }): Promise<ResearchSessionListResponse> => {
    const response = await apiClient.get('/api/v1/research/sessions', { params })
    return response.data.data
  },

  /**
   * Update a research session
   */
  updateSession: async (
    sessionId: string,
    data: ResearchSessionUpdate
  ): Promise<ResearchSession> => {
    const response = await apiClient.put(`/api/v1/research/sessions/${sessionId}`, data)
    return response.data.data.session
  },

  /**
   * Delete a research session
   */
  deleteSession: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/research/sessions/${sessionId}`)
  },

  /**
   * Start a research session
   */
  startSession: async (sessionId: string): Promise<ResearchSession> => {
    const response = await apiClient.post(`/api/v1/research/sessions/${sessionId}/start`)
    return response.data.data.session
  },

  /**
   * Cancel a research session
   */
  cancelSession: async (sessionId: string): Promise<ResearchSession> => {
    const response = await apiClient.post(`/api/v1/research/sessions/${sessionId}/cancel`)
    return response.data.data.session
  },
}
