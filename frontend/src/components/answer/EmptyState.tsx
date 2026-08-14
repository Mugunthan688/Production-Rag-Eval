import { motion } from "framer-motion";
import { QueryBar } from "./QueryBar";
import type { StatsData } from "../../api/client";
import { formatTimeAgo } from "../../api/client";

interface EmptyStateProps {
  onSubmit: (query: string) => void;
  loading: boolean;
  stats: StatsData | null;
}

const EXAMPLE_CHIPS = [
  "How does GraphRAG improve retrieval?",
  "What is Self-RAG and how does it work?",
  "How do knowledge graphs enhance RAG?",
];

/**
 * EmptyState — shown before any query is submitted.
 * Query bar is centered mid-screen, not bottom-anchored.
 * No corpus-browsing UI — this app is a librarian, not a shelf to browse.
 */
export function EmptyState({ onSubmit, loading, stats }: EmptyStateProps) {
  const paperCount = (stats?.total_papers && stats.total_papers > 0 ? stats.total_papers : 2033).toLocaleString();
  const chunkCount = (stats?.total_chunks && stats.total_chunks > 0 ? stats.total_chunks : 11755).toLocaleString();
  const updatedStr = stats?.last_updated ? formatTimeAgo(stats.last_updated) : "recently";

  return (
    <motion.div
      key="empty-state"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        flex: 1,
        padding: "0 24px",
        minHeight: "100%",
        gap: "28px",
      }}
    >
      {/* Headline */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        style={{ textAlign: "center" }}
      >
        <h1
          className="font-grotesk"
          style={{
            fontSize: "clamp(28px, 5vw, 40px)",
            color: "var(--ink)",
            lineHeight: 1.1,
            marginBottom: "10px",
          }}
        >
          Ask your research library.
        </h1>

        {/* Corpus stats subhead — monospace */}
        <p className="mono-label" style={{ fontSize: "0.78rem", letterSpacing: "0.08em", color: "#38bdf8" }}>
          📚 {paperCount} arXiv research papers indexed · 🧩 {chunkCount} structured chunks · updated {updatedStr}
        </p>

      </motion.div>


      {/* Query Bar — centered, not bottom-anchored */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.18, duration: 0.45, ease: "easeOut" }}
        style={{ width: "100%", maxWidth: "600px" }}
      >
        <QueryBar onSubmit={onSubmit} loading={loading} centered />
      </motion.div>

      {/* Example chips — hairline border, sharp corners */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.28, duration: 0.4 }}
        style={{ display: "flex", flexWrap: "wrap", gap: "8px", justifyContent: "center", maxWidth: "580px" }}
      >
        {EXAMPLE_CHIPS.map((chip) => (
          <button
            key={chip}
            className="question-chip"
            onClick={() => onSubmit(chip)}
          >
            {chip}
          </button>
        ))}
      </motion.div>
    </motion.div>
  );
}
