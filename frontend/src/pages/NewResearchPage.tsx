/**
 * AI Council - New Research Page
 * Form to create a new research session
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useResearchStore } from '../store/researchStore'
import { ResearchCategory } from '../types/research'
import { Button } from '../components/Button'

export const NewResearchPage = () => {
  const navigate = useNavigate()
  const { createSession, loading, error, clearError } = useResearchStore()

  const [formData, setFormData] = useState({
    title: '',
    question: '',
    category: ResearchCategory.GENERAL,
    priority: 'medium',
    selected_agents: [] as string[],
    enable_rag: false,
    enable_review: true,
    enable_citations: true,
    selected_document_ids: [] as string[],
  })

  const availableAgents = [
    { id: 'research_agent', name: 'Research Agent' },
    { id: 'technical_agent', name: 'Technical Agent' },
    { id: 'cost_agent', name: 'Cost/Infrastructure Agent' },
    { id: 'data_agent', name: 'Data Analysis Agent' },
    { id: 'product_agent', name: 'Product/Business Agent' },
    { id: 'security_agent', name: 'Risk/Security Agent' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    try {
      const session = await createSession(formData)
      navigate(`/research/${session.id}`)
    } catch (err) {
      console.error('Failed to create session:', err)
    }
  }

  const handleAgentToggle = (agentId: string) => {
    setFormData((prev) => ({
      ...prev,
      selected_agents: prev.selected_agents.includes(agentId)
        ? prev.selected_agents.filter((id) => id !== agentId)
        : [...prev.selected_agents, agentId],
    }))
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">New Research Session</h1>
        <p className="text-gray-600 mt-2">Create a new multi-agent research session</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Title *
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Microservices vs Monolith Analysis"
            required
          />
        </div>

        {/* Question */}
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
            Research Question *
          </label>
          <textarea
            id="question"
            value={formData.question}
            onChange={(e) => setFormData({ ...formData, question: e.target.value })}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="What specific question do you want to research?"
            required
          />
        </div>

        {/* Category */}
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            id="category"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value as ResearchCategory })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={ResearchCategory.GENERAL}>General</option>
            <option value={ResearchCategory.SOFTWARE_ARCHITECTURE}>Software Architecture</option>
            <option value={ResearchCategory.BUSINESS_STRATEGY}>Business Strategy</option>
            <option value={ResearchCategory.PRODUCT_RESEARCH}>Product Research</option>
            <option value={ResearchCategory.DATA_ANALYSIS}>Data Analysis</option>
            <option value={ResearchCategory.SECURITY}>Security</option>
            <option value={ResearchCategory.TECHNOLOGY}>Technology</option>
            <option value={ResearchCategory.MARKET_RESEARCH}>Market Research</option>
          </select>
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
            Priority
          </label>
          <select
            id="priority"
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        {/* Agents */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Agents
          </label>
          <div className="grid grid-cols-2 gap-3">
            {availableAgents.map((agent) => (
              <label key={agent.id} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.selected_agents.includes(agent.id)}
                  onChange={() => handleAgentToggle(agent.id)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{agent.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Options */}
        <div className="space-y-3">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.enable_rag}
              onChange={(e) => setFormData({ ...formData, enable_rag: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Enable RAG (Retrieval-Augmented Generation)</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.enable_review}
              onChange={(e) => setFormData({ ...formData, enable_review: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Enable Critical Review</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.enable_citations}
              onChange={(e) => setFormData({ ...formData, enable_citations: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Enable Citations</span>
          </label>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/research')}
          >
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            Create Session
          </Button>
        </div>
      </form>
    </div>
  )
}
