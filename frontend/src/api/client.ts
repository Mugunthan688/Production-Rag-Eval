const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://production-rag-eval.onrender.com";



export interface ChunkData {
  chunk_id: string;
  paper_id: string;
  score: number;
  text: string;
  paper_title: string;
  paper_authors: string[];
  paper_categories: string[];
  paper_pdf_url: string;
}

export interface ConfidenceReport {
  retrieval_confidence: number;
  source_diversity: number;
  score_distribution: {
    mean: number;
    std: number;
    top1_gap: number;
    entropy: number;
    normalized_entropy: number;
  };
  answer_grounding: number;
  hallucination_risk: "low" | "medium" | "high";
  composite_confidence: number;
  confidence_label: "HIGH" | "MEDIUM" | "LOW";
  explanation: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  chunks_used: ChunkData[];
  latency_ms: number;
  papers_searched: number;
  confidence: ConfidenceReport;
}

export interface PaperData {
  id: string;
  title: string;
  authors: string[];
  categories: string[];
  submitted_date: string | null;
  pdf_url: string;
  abstract: string;
  chunk_count: number;
}

export interface StatsData {
  total_papers: number;
  total_chunks: number;
  last_updated: string | null;
  top_categories: { category: string; count: number }[];
}

export interface FeedbackAnalytics {
  lowest_rated_queries: {
    id: number;
    query: string;
    answer: string;
    rating: number;
    comments: string | null;
  }[];
  problematic_chunks: unknown[];
}

/** A single conversation turn stored in history */
export interface HistoryEntry {
  id: string;
  query: string;
  answer: string;
  chunks: ChunkData[];
  confidence: ConfidenceReport;
  latency_ms: number;
  papers_searched: number;
  timestamp: number; // Date.now()
}

export async function executeQuery(params: {
  query: string;
  chunking_strategy?: string;
  hybrid_search?: boolean;
  reranker?: boolean;
  query_rewriting?: boolean;
}): Promise<QueryResponse> {
  const resp = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: params.query,
      chunking_strategy: params.chunking_strategy ?? "recursive",
      hybrid_search: params.hybrid_search ?? true,
      reranker: params.reranker ?? true,
      query_rewriting: params.query_rewriting ?? true,
    }),
  });
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export async function fetchPapers(limit = 200): Promise<PaperData[]> {
  const resp = await fetch(`${API_BASE}/papers?limit=${limit}`);
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export async function fetchStats(): Promise<StatsData> {
  const resp = await fetch(`${API_BASE}/papers/stats`);
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export async function fetchFeedbackAnalytics(): Promise<FeedbackAnalytics> {
  const resp = await fetch(`${API_BASE}/feedback/analytics`);
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export async function submitFeedback(data: {
  query: string;
  answer: string;
  chunks_used: string[];
  rating: number;
  comments: string;
}): Promise<void> {
  await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

/** Format seconds-ago as a human-readable string */
export function formatTimeAgo(isoDate: string | null): string {
  if (!isoDate) return "unknown";
  const diff = (Date.now() - new Date(isoDate).getTime()) / 1000;
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`;
  return `${Math.round(diff / 86400)}d ago`;
}
