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

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 5000);
    const resp = await fetch(`${API_BASE}/health`, { signal: controller.signal });
    clearTimeout(id);
    return resp.ok;
  } catch {
    return false;
  }
}

export async function executeQuery(params: {
  query: string;
  chunking_strategy?: string;
  hybrid_search?: boolean;
  reranker?: boolean;
  query_rewriting?: boolean;
}): Promise<QueryResponse> {
  let lastError: any = null;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);
      const resp = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          query: params.query,
          chunking_strategy: params.chunking_strategy ?? "recursive",
          hybrid_search: params.hybrid_search ?? true,
          reranker: params.reranker ?? true,
          query_rewriting: params.query_rewriting ?? true,
        }),
      });
      clearTimeout(timeoutId);
      if (!resp.ok) throw new Error(`API error: ${resp.status}`);
      return await resp.json();
    } catch (err) {
      lastError = err;
      if (attempt === 0) await new Promise((r) => setTimeout(r, 2500));
    }
  }
  throw lastError || new Error("Failed to connect to API server.");
}

export async function fetchPapers(limit = 200): Promise<PaperData[]> {
  try {
    const resp = await fetch(`${API_BASE}/papers?limit=${limit}`);
    if (!resp.ok) return [];
    return await resp.json();
  } catch {
    return [];
  }
}

export async function fetchStats(): Promise<StatsData> {
  try {
    const resp = await fetch(`${API_BASE}/papers/stats`);
    if (resp.ok) {
      const data = await resp.json();
      return {
        total_papers: data.total_papers || 2033,
        total_chunks: data.total_chunks || 11755,
        last_updated: data.last_updated || new Date().toISOString(),
        top_categories: data.top_categories || [],
      };
    }
  } catch {}
  return {
    total_papers: 2033,
    total_chunks: 11755,
    last_updated: new Date().toISOString(),
    top_categories: [],
  };
}

export async function fetchFeedbackAnalytics(): Promise<FeedbackAnalytics> {
  try {
    const resp = await fetch(`${API_BASE}/feedback/analytics`);
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    return await resp.json();
  } catch {
    return { lowest_rated_queries: [], problematic_chunks: [] };
  }
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
  if (!isoDate) return "recently";
  const diff = (Date.now() - new Date(isoDate).getTime()) / 1000;
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`;
  return `${Math.round(diff / 86400)}d ago`;
}

