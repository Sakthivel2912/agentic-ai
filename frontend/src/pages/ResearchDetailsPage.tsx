/**
 * AI Council - Research Details Page
 * Display full details of a research session with real-time updates
 */
import { Children, isValidElement, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useResearchStore } from '../store/researchStore'
import { useSSE } from '../hooks/useSSE'
import { SessionStatus } from '../types/research'
import { Button } from '../components/Button'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { MermaidDiagram } from '../components/MermaidDiagram'
import { Download } from 'lucide-react'

const cleanInlineMarkdown = (text: string) => text
  .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
  .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '$1 ($2)')
  .replace(/\\([^\w\s])/g, '$1')
  .replace(/(`{1,3})(.*?)\1/g, '$2')
  .replace(/(\*\*|__)(.*?)\1/g, '$2')
  .replace(/([*_~])/g, '')

const normalizePdfText = (text: string) => text
  .replace(/[\u2010-\u2015\u2212]/g, '-')
  .replace(/[\u2018\u2019]/g, "'")
  .replace(/[\u201C\u201D]/g, '"')
  .replace(/[\u00A0\u202F]/g, ' ')
  .replace(/[\u00B5\u03BC]/g, 'mu')
  .replace(/[\u03B5\u03F5]/g, 'epsilon')
  .replace(/\u03B4/g, 'delta')
  .replace(/\u03B1/g, 'alpha')
  .replace(/\u03C3/g, 'sigma')
  .replace(/\u2264/g, '<=')
  .replace(/\u2265/g, '>=')
  .replace(/\u00D7/g, 'x')
  .replace(/\u2192/g, '->')

const parseTableCells = (line: string) => line
  .trim()
  .replace(/^\|/, '')
  .replace(/\|$/, '')
  .split('|')
  .map((cell) => normalizePdfText(cleanInlineMarkdown(cell.trim())))

const isTableSeparator = (line: string) =>
  /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line)

const svgToPng = async (svg: string) => {
  const objectUrl = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }))
  try {
    const image = new Image()
    image.src = objectUrl
    await image.decode()
    const canvas = document.createElement('canvas')
    canvas.width = image.naturalWidth * 2
    canvas.height = image.naturalHeight * 2
    const context = canvas.getContext('2d')
    if (!context) throw new Error('Could not render report diagram')
    context.scale(2, 2)
    context.drawImage(image, 0, 0)
    return { data: canvas.toDataURL('image/png'), width: image.naturalWidth, height: image.naturalHeight }
  } finally {
    URL.revokeObjectURL(objectUrl)
  }
}

const exportResearchPdf = async (session: NonNullable<ReturnType<typeof useResearchStore.getState>['currentSession']>) => {
  const finalAnswer = session.final_answer
  if (!finalAnswer) return

  const { jsPDF } = await import('jspdf')
  const [{ default: autoTable }, { default: mermaid }] = await Promise.all([
    import('jspdf-autotable'),
    import('mermaid'),
  ])
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'neutral',
    htmlLabels: false,
  })
  const hasWideTables = finalAnswer.split('\n').some((line, index, allLines) =>
    line.includes('|') && allLines[index + 1] !== undefined && isTableSeparator(allLines[index + 1]),
  )
  const pdf = new jsPDF({
    unit: 'pt',
    format: 'a4',
    orientation: hasWideTables ? 'landscape' : 'portrait',
  })
  const margin = 52
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const textWidth = pageWidth - margin * 2
  let cursorY = 54

  const addLines = (text: string, fontSize: number, bold = false, gapAfter = 8) => {
    pdf.setFont('helvetica', bold ? 'bold' : 'normal')
    pdf.setFontSize(fontSize)
    pdf.setCharSpace(0)
    const normalizedText = normalizePdfText(text)
    const lines = pdf.splitTextToSize(normalizedText, textWidth) as string[]
    const lineHeight = fontSize * 1.45

    for (const line of lines) {
      if (cursorY + lineHeight > pageHeight - margin) {
        pdf.addPage()
        cursorY = margin
      }
      pdf.text(line, margin, cursorY, { charSpace: 0 })
      cursorY += lineHeight
    }
    cursorY += gapAfter
  }

  pdf.setTextColor(18, 60, 82)
  addLines('AI COUNCIL  /  RESEARCH REPORT', 9, true, 14)
  addLines(cleanInlineMarkdown(session.title), 20, true, 12)
  addLines('Research question', 11, true, 4)
  addLines(cleanInlineMarkdown(session.question), 11, false, 14)
  addLines(`Created ${new Date(session.created_at).toLocaleString()}`, 9, false, 20)

  const lines = finalAnswer.split('\n')
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index]
    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+)$/)
    const listItem = line.match(/^\s*(?:[-*+] |\d+[.)] )(.+)$/)

    if (line.trim().startsWith('```')) {
      const language = line.trim().slice(3).trim().toLowerCase()
      const codeLines: string[] = []
      index += 1
      while (index < lines.length && !lines[index].trim().startsWith('```')) {
        codeLines.push(lines[index])
        index += 1
      }
      if (language === 'mermaid') {
        try {
          const { svg } = await mermaid.render(`pdf-diagram-${index}`, codeLines.join('\n'))
          const image = await svgToPng(svg)
          const maxWidth = textWidth
          const maxHeight = pageHeight - margin * 2
          const scale = Math.min(maxWidth / image.width, maxHeight / image.height, 1)
          const imageWidth = image.width * scale
          const imageHeight = image.height * scale
          if (cursorY + imageHeight > pageHeight - margin) {
            pdf.addPage()
            cursorY = margin
          }
          pdf.addImage(image.data, 'PNG', margin, cursorY, imageWidth, imageHeight)
          cursorY += imageHeight + 12
        } catch {
          addLines(codeLines.join(' '), 8, false, 8)
        }
      } else {
        addLines(codeLines.join('\n'), 8, false, 8)
      }
      continue
    }

    if (line.includes('|') && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
      const head = [parseTableCells(line)]
      const body: string[][] = []
      index += 2
      while (index < lines.length && lines[index].includes('|') && lines[index].trim()) {
        body.push(parseTableCells(lines[index]))
        index += 1
      }
      index -= 1
      const startY = cursorY > pageHeight - margin ? margin : cursorY
      autoTable(pdf, {
        head,
        body,
        startY,
        margin: { left: margin, right: margin, top: margin, bottom: margin },
        tableWidth: 'auto',
        theme: 'grid',
        styles: {
          font: 'helvetica',
          fontSize: 7,
          cellPadding: 4,
          overflow: 'linebreak',
          valign: 'top',
          minCellHeight: 18,
        },
        headStyles: { fillColor: [18, 60, 82], textColor: [255, 255, 255] },
        alternateRowStyles: { fillColor: [242, 247, 249] },
        didParseCell: () => {
          pdf.setCharSpace(0)
        },
      })
      const finalY = (pdf as typeof pdf & { lastAutoTable?: { finalY: number } }).lastAutoTable?.finalY
      cursorY = (finalY ?? startY) + 14
      continue
    }

    if (heading) {
      addLines(cleanInlineMarkdown(heading[2]), heading[1].length === 1 ? 15 : 12, true, 5)
    } else if (listItem) {
      addLines(`- ${cleanInlineMarkdown(listItem[1])}`, 10, false, 3)
    } else if (line.trim()) {
      addLines(cleanInlineMarkdown(line.trim()), 10, false, 4)
    } else {
      cursorY += 5
    }
  }

  if (session.sources.length > 0) {
    if (cursorY + 40 > pageHeight - margin) {
      pdf.addPage()
      cursorY = margin
    }
    pdf.setTextColor(18, 60, 82)
    addLines('Sources', 15, true, 8)
    session.sources.forEach((source, index) => {
      const sourceText = `[${index + 1}] ${cleanInlineMarkdown(source.title || `Source ${index + 1}`)}${source.url ? ` - ${source.url}` : ''}`
      addLines(sourceText, 9, false, 4)
      if (source.content) {
        addLines(cleanInlineMarkdown(source.content.slice(0, 600)), 8, false, 7)
      }
    })
  }

  const pageCount = pdf.getNumberOfPages()
  for (let page = 1; page <= pageCount; page += 1) {
    pdf.setPage(page)
    pdf.setFont('helvetica', 'normal')
    pdf.setFontSize(8)
    pdf.setTextColor(100, 116, 128)
    pdf.setCharSpace(0)
    pdf.text(`AI Council  |  ${page} / ${pageCount}`, pageWidth - margin, pageHeight - 24, { align: 'right', charSpace: 0 })
  }

  const filename = cleanInlineMarkdown(session.title)
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '-')
    .trim()
    .replace(/\s+/g, '-')
    .slice(0, 80) || 'research-answer'
  pdf.save(`${filename}.pdf`)
}

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
      if (id) {
        getSession(id).catch((err) => {
          console.error('Failed to refresh completed research:', err)
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
            {(currentSession.status === SessionStatus.DRAFT || currentSession.status === SessionStatus.FAILED) && (
              <Button variant="primary" onClick={handleStart} loading={loading}>
                {currentSession.status === SessionStatus.FAILED ? 'Retry Research' : 'Start Research'}
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
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-lg font-medium text-gray-900">Final Answer</h2>
            <button
              type="button"
              onClick={() => {
                void exportResearchPdf(currentSession).catch((exportError) => {
                  console.error('Failed to export research PDF:', exportError)
                })
              }}
              title="Download answer as PDF"
              aria-label="Download answer as PDF"
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-[#d7e3e8] text-[#315469] transition hover:border-[#42cdb3] hover:bg-[#e8faf5] focus:outline-none focus:ring-2 focus:ring-[#42cdb3]"
            >
              <Download className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
          <div className="prose max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ children }) => (
                  <div className="my-5 overflow-x-auto rounded-lg border border-slate-200">
                    <table className="w-full border-collapse text-left text-sm">{children}</table>
                  </div>
                ),
                thead: ({ children }) => <thead className="bg-[#123c52] text-white">{children}</thead>,
                th: ({ children }) => <th className="border border-slate-200 px-3 py-2 font-semibold">{children}</th>,
                td: ({ children }) => <td className="border border-slate-200 px-3 py-2 align-top">{children}</td>,
                tr: ({ children }) => <tr className="even:bg-slate-50">{children}</tr>,
                pre: ({ children }) => {
                  const [codeChild] = Children.toArray(children)
                  const isMermaid = isValidElement<{ className?: string }>(codeChild)
                    && codeChild.props.className?.includes('language-mermaid')
                  return isMermaid
                    ? <>{children}</>
                    : <pre className="overflow-x-auto rounded-lg bg-slate-50 p-4 text-sm">{children}</pre>
                },
                code: ({ className, children }) => {
                  const language = /language-(\w+)/.exec(className || '')?.[1]
                  if (language === 'mermaid') {
                    return <MermaidDiagram chart={String(children).replace(/\n$/, '')} />
                  }
                  return <code className={className}>{children}</code>
                },
              }}
              className="prose max-w-none text-gray-700"
            >
              {currentSession.final_answer}
            </ReactMarkdown>
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
                {source.content && (
                  <p className="mt-2 text-sm text-gray-600">{source.content}</p>
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
