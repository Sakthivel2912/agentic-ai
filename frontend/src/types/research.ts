/**
 * AI Council - Research Session Types
 */

export enum SessionStatus {
  DRAFT = 'draft',
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum ResearchCategory {
  GENERAL = 'general',
  SOFTWARE_ARCHITECTURE = 'software_architecture',
  BUSINESS_STRATEGY = 'business_strategy',
  PRODUCT_RESEARCH = 'product_research',
  DATA_ANALYSIS = 'data_analysis',
  SECURITY = 'security',
  TECHNOLOGY = 'technology',
  MARKET_RESEARCH = 'market_research'
}

export interface ResearchSession {
  id: string;
  user_id: string;
  title: string;
  question: string;
  category: string;
  priority: string;
  selected_agents: string[];
  enable_rag: boolean;
  enable_review: boolean;
  enable_citations: boolean;
  selected_document_ids: string[];
  status: string;
  current_stage: string;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  updated_at: string;
  agent_outputs: Record<string, any>;
  reviewer_feedback?: Record<string, any>;
  final_answer?: string;
  sources: Array<Record<string, any>>;
  error_message?: string;
  metadata: Record<string, any>;
}

export interface ResearchSessionCreate {
  title: string;
  question: string;
  category?: ResearchCategory;
  priority?: string;
  selected_agents?: string[];
  enable_rag?: boolean;
  enable_review?: boolean;
  enable_citations?: boolean;
  selected_document_ids?: string[];
}

export interface ResearchSessionUpdate {
  title?: string;
  question?: string;
  category?: ResearchCategory;
  priority?: string;
  selected_agents?: string[];
  enable_rag?: boolean;
  enable_review?: boolean;
  enable_citations?: boolean;
  selected_document_ids?: string[];
}

export interface ResearchSessionListResponse {
  sessions: ResearchSession[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SessionStartRequest {
  session_id: string;
}

export interface AgentOutput {
  agent_id: string;
  agent_name: string;
  status: string;
  output?: string;
  error?: string;
  started_at?: string;
  completed_at?: string;
}

export interface Source {
  id: string;
  title: string;
  content: string;
  url?: string;
  document_id?: string;
  page_number?: number;
  score?: number;
}
