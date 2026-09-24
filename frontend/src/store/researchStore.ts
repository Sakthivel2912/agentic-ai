/**
 * AI Council - Research Session Store
 * Zustand store for research session state management
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { researchApi } from '../api/research.api'
import {
  ResearchSession,
  ResearchSessionCreate,
  ResearchSessionUpdate,
  ResearchSessionListResponse,
} from '../types/research'

interface ResearchState {
  sessions: ResearchSession[]
  currentSession: ResearchSession | null
  loading: boolean
  error: string | null
  total: number
  page: number
  page_size: number
  total_pages: number
  
  // Actions
  createSession: (data: ResearchSessionCreate) => Promise<ResearchSession>
  getSession: (sessionId: string) => Promise<ResearchSession>
  listSessions: (params?: {
    status?: string
    category?: string
    page?: number
    page_size?: number
  }) => Promise<void>
  updateSession: (sessionId: string, data: ResearchSessionUpdate) => Promise<ResearchSession>
  deleteSession: (sessionId: string) => Promise<void>
  startSession: (sessionId: string) => Promise<ResearchSession>
  cancelSession: (sessionId: string) => Promise<ResearchSession>
  setCurrentSession: (session: ResearchSession | null) => void
  clearError: () => void
}

export const useResearchStore = create<ResearchState>()(
  persist(
    (set) => ({
      sessions: [],
      currentSession: null,
      loading: false,
      error: null,
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,

      createSession: async (data: ResearchSessionCreate) => {
        set({ loading: true, error: null })
        try {
          const session = await researchApi.createSession(data)
          set((state) => ({
            sessions: [session, ...state.sessions],
            currentSession: session,
            loading: false,
          }))
          return session
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to create session'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      getSession: async (sessionId: string) => {
        set({ loading: true, error: null })
        try {
          const session = await researchApi.getSession(sessionId)
          set({ currentSession: session, loading: false })
          return session
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to get session'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      listSessions: async (params) => {
        set({ loading: true, error: null })
        try {
          const response: ResearchSessionListResponse = await researchApi.listSessions(params)
          set({
            sessions: response.sessions,
            total: response.total,
            page: response.page,
            page_size: response.page_size,
            total_pages: response.total_pages,
            loading: false,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to list sessions'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      updateSession: async (sessionId: string, data: ResearchSessionUpdate) => {
        set({ loading: true, error: null })
        try {
          const session = await researchApi.updateSession(sessionId, data)
          set((state) => ({
            sessions: state.sessions.map((s) => (s.id === sessionId ? session : s)),
            currentSession: state.currentSession?.id === sessionId ? session : state.currentSession,
            loading: false,
          }))
          return session
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to update session'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      deleteSession: async (sessionId: string) => {
        set({ loading: true, error: null })
        try {
          await researchApi.deleteSession(sessionId)
          set((state) => ({
            sessions: state.sessions.filter((s) => s.id !== sessionId),
            currentSession: state.currentSession?.id === sessionId ? null : state.currentSession,
            loading: false,
          }))
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to delete session'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      startSession: async (sessionId: string) => {
        set({ loading: true, error: null })
        try {
          const session = await researchApi.startSession(sessionId)
          set((state) => ({
            sessions: state.sessions.map((s) => (s.id === sessionId ? session : s)),
            currentSession: state.currentSession?.id === sessionId ? session : state.currentSession,
            loading: false,
          }))
          return session
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to start session'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      cancelSession: async (sessionId: string) => {
        set({ loading: true, error: null })
        try {
          const session = await researchApi.cancelSession(sessionId)
          set((state) => ({
            sessions: state.sessions.map((s) => (s.id === sessionId ? session : s)),
            currentSession: state.currentSession?.id === sessionId ? session : state.currentSession,
            loading: false,
          }))
          return session
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Failed to cancel session'
          set({ error: errorMessage, loading: false })
          throw error
        }
      },

      setCurrentSession: (session: ResearchSession | null) => {
        set({ currentSession: session })
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'research-storage',
      partialize: (state) => ({
        sessions: state.sessions,
        currentSession: state.currentSession,
      }),
    }
  )
)
