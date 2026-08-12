import { useState, useRef, useEffect, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { BlueprintGrid } from "../fx/BlueprintGrid";
import { HistoryRail } from "./HistoryRail";
import { EvidenceRail } from "../evidence/EvidenceRail";
import { EmptyState } from "../answer/EmptyState";
import { QueryBar } from "../answer/QueryBar";
import { StreamingAnswer } from "../answer/StreamingAnswer";
import { ConstellationTrace, type TraceTarget } from "../fx/ConstellationTrace";
import {
  executeQuery,
  fetchStats,
  type QueryResponse,
  type StatsData,
  type HistoryEntry,
  type ChunkData,
} from "../../api/client";

interface ConversationTurn {
  id: string;
  role: "user" | "assistant";
  content: string;
  chunks?: ChunkData[];
  latencyMs?: number;
  papersSearched?: number;
  confidence?: QueryResponse["confidence"];
}

/**
 * AppShell — top-level three-column layout for Marginalia.
 *
 *  ┌──────────────┬─────────────────────────────┬──────────────┐
 *  │  HistoryRail │      Answer Column           │ EvidenceRail │
 *  │  (200px)     │   (fluid, max 680px)         │  (288px)     │
 *  └──────────────┴─────────────────────────────┴──────────────┘
 *
 * State managed here:
 * - conversation turns
 * - evidence chunks for the current turn
 * - active constellation trace (citation ↔ card)
 * - corpus stats (papers count, last updated)
 * - history entries (stored in state, persisted to localStorage)
 */
export function AppShell() {
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeChunkId, setActiveChunkId] = useState<string | null>(null);
  const [evidenceChunks, setEvidenceChunks] = useState<ChunkData[]>([]);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);
  const [corpusActive, setCorpusActive] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);

  // Load stats on mount
  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
  }, []);

  // Load history from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem("marginalia-history");
      if (stored) setHistory(JSON.parse(stored) as HistoryEntry[]);
    } catch {
      // ignore
    }
  }, []);

  // Auto-scroll feed to bottom on new messages
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [turns]);

  const handleSubmit = useCallback(async (query: string) => {
    const userTurn: ConversationTurn = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
    };

    setTurns((prev) => [...prev, userTurn]);
    setEvidenceChunks([]);
    setActiveChunkId(null);
    setLoading(true);
    setCorpusActive(true);

    try {
      const data: QueryResponse = await executeQuery({ query });

      const aiTurn: ConversationTurn = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        chunks: data.chunks_used,
        latencyMs: data.latency_ms,
        papersSearched: data.papers_searched,
        confidence: data.confidence,
      };

      setTurns((prev) => [...prev, aiTurn]);
      setEvidenceChunks(data.chunks_used);
      setActiveHistoryId(aiTurn.id);

      // Persist to history
      const entry: HistoryEntry = {
        id: aiTurn.id,
        query,
        answer: data.answer,
        chunks: data.chunks_used,
        confidence: data.confidence,
        latency_ms: data.latency_ms,
        papers_searched: data.papers_searched,
        timestamp: Date.now(),
      };

      setHistory((prev) => {
        const next = [...prev, entry].slice(-50); // keep last 50
        localStorage.setItem("marginalia-history", JSON.stringify(next));
        return next;
      });
    } catch (err) {
      const errTurn: ConversationTurn = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: `**Connection error** — could not reach the API server.\n\nMake sure the FastAPI backend is running at \`https://production-rag-eval.onrender.com\`.\n\n\`\`\`\n${err}\n\`\`\``,

      };
      setTurns((prev) => [...prev, errTurn]);
    } finally {
      setLoading(false);
      setTimeout(() => setCorpusActive(false), 800);
    }
  }, []);

  // Restore a history entry
  const handleHistorySelect = useCallback((entry: HistoryEntry) => {
    setTurns([
      { id: `user-${entry.id}`, role: "user", content: entry.query },
      {
        id: entry.id,
        role: "assistant",
        content: entry.answer,
        chunks: entry.chunks,
        latencyMs: entry.latency_ms,
        papersSearched: entry.papers_searched,
        confidence: entry.confidence,
      },
    ]);
    setEvidenceChunks(entry.chunks);
    setActiveHistoryId(entry.id);
    setActiveChunkId(null);
  }, []);

  // Build constellation trace targets from current evidence
  const traceTargets: TraceTarget[] = evidenceChunks.map((c) => ({
    markerId: `citation-marker-${c.chunk_id}`,
    cardId: `evidence-card-${c.chunk_id}`,
    weak: c.score < 0.55,
  }));

  const isEmpty = turns.length === 0;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        backgroundColor: "var(--canvas)",
        position: "relative",
      }}
    >
      {/* Blueprint grid background */}
      <BlueprintGrid active={corpusActive} />

      {/* Constellation trace SVG overlay */}
      <ConstellationTrace traces={traceTargets} activeTraceId={activeChunkId} />

      {/* ── Column 1: History Rail ── */}
      <HistoryRail
        history={history}
        activeId={activeHistoryId}
        onSelect={handleHistorySelect}
      />

      {/* ── Column 2: Answer Column ── */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* Marginalia logotype bar */}
        <header style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 24px",
          borderBottom: "1px solid var(--border)",
          flexShrink: 0,
        }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: "10px" }}>
            <span className="font-grotesk" style={{ fontSize: "1rem", color: "var(--ink)", letterSpacing: "-0.04em" }}>
              Marginalia
            </span>
            <span className="mono-label" style={{ fontSize: "0.58rem" }}>
              Research Intelligence
            </span>
          </div>
          {stats && (
            <span className="mono-label" style={{ fontSize: "0.58rem" }}>
              {stats.total_papers?.toLocaleString()} papers
            </span>
          )}
        </header>

        {/* Feed + empty state */}
        <div
          ref={feedRef}
          style={{
            flex: 1,
            overflowY: "auto",
            overflowX: "hidden",
            display: "flex",
            flexDirection: "column",
            padding: isEmpty ? "0" : "32px 40px 24px 40px",
            gap: isEmpty ? "0" : "28px",
            maxWidth: "100%",
          }}
        >
          <AnimatePresence mode="wait">
            {isEmpty ? (
              <EmptyState
                key="empty"
                onSubmit={handleSubmit}
                loading={loading}
                stats={stats}
              />
            ) : (
              <motion.div
                key="feed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ display: "flex", flexDirection: "column", gap: "28px", maxWidth: "680px", width: "100%" }}
              >
                {turns.map((turn) => (
                  <div key={turn.id}>
                    {turn.role === "user" ? (
                      /* User query bubble */
                      <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ type: "spring", stiffness: 350, damping: 28 }}
                        style={{ display: "flex", justifyContent: "flex-end" }}
                      >
                        <div className="user-query">{turn.content}</div>
                      </motion.div>
                    ) : (
                      /* AI answer */
                      <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ type: "spring", stiffness: 300, damping: 30, delay: 0.05 }}
                      >
                        <StreamingAnswer
                          content={turn.content}
                          chunks={turn.chunks ?? []}
                          latencyMs={turn.latencyMs}
                          papersSearched={turn.papersSearched}
                          confidence={turn.confidence}
                          activeChunkId={activeChunkId}
                          onActivateCitation={setActiveChunkId}
                        />
                      </motion.div>
                    )}
                  </div>
                ))}

                {/* Loading placeholder — only during retrieval */}
                {loading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mono-label"
                    style={{ fontSize: "0.62rem", letterSpacing: "0.1em", color: "var(--cobalt)", animationDelay: "0.2s" }}
                  >
                    RETRIEVING…
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Bottom-anchored QueryBar — only shown when conversation started */}
        {!isEmpty && (
          <div
            style={{
              flexShrink: 0,
              padding: "12px 40px 20px 40px",
              borderTop: "1px solid var(--border)",
              display: "flex",
              justifyContent: "flex-start",
            }}
          >
            <QueryBar onSubmit={handleSubmit} loading={loading} />
          </div>
        )}
      </div>

      {/* ── Column 3: Evidence Rail ── */}
      <EvidenceRail
        chunks={evidenceChunks}
        highlightedChunkId={activeChunkId}
        onHighlight={setActiveChunkId}
      />
    </div>
  );
}
