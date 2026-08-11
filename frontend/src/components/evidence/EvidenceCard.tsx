import { useState } from "react";
import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import { RelevanceBar } from "../fx/RelevanceBar";
import type { ChunkData } from "../../api/client";

interface EvidenceCardProps {
  chunk: ChunkData;
  index: number;                // card index (0-based)
  isHighlighted: boolean;       // true when its citation marker is active
  onHighlight: (chunkId: string | null) => void;
}

/** Deterministic ±1deg rotation seeded by the card's chunk_id */
function seedRotation(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) & 0xffff;
  }
  // Map 0-65535 → -1 to +1
  return ((hash / 65535) * 2 - 1) * 1;
}

const WEAK_THRESHOLD = 0.55;

export function EvidenceCard({ chunk, index, isHighlighted, onHighlight }: EvidenceCardProps) {
  const [linkBroken, setLinkBroken] = useState(false);
  const rotation = seedRotation(chunk.chunk_id);
  const isWeak = chunk.score < WEAK_THRESHOLD;
  const matchPercent = Math.round(chunk.score * 100);

  // Passage: trim to ~250 chars for readability
  const passage = chunk.text.length > 280
    ? chunk.text.slice(0, 280).trimEnd() + "…"
    : chunk.text;

  return (
    <motion.article
      id={`evidence-card-${chunk.chunk_id}`}
      className={`evidence-card grain-overlay ${isWeak ? "evidence-card--weak" : ""} ${isHighlighted ? "elevated" : ""}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{
        opacity: 1,
        y: 0,
        rotate: rotation,
      }}
      whileHover={{ rotate: 0, scale: 1.005 }}
      transition={{ delay: index * 0.06, type: "spring", stiffness: 300, damping: 28 }}
      style={{ marginBottom: "10px", position: "relative" }}
      onMouseEnter={() => onHighlight(chunk.chunk_id)}
      onMouseLeave={() => onHighlight(null)}
    >
      {/* ── Header row ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px", gap: "8px" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Category badge + arXiv ID */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
            {chunk.paper_categories[0] && (
              <span className="mono-label" style={{ color: "var(--cobalt)", borderColor: "var(--cobalt-dim)", border: "1px solid", padding: "1px 4px", borderRadius: "1px" }}>
                {chunk.paper_categories[0]}
              </span>
            )}
            {isWeak && <span className="tag-weak-match">Weak Match</span>}
          </div>
          {/* Title — bold serif */}
          <p style={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 700,
            fontSize: "0.78rem",
            lineHeight: 1.35,
            color: "var(--ink)",
            letterSpacing: "-0.01em",
            marginBottom: "2px",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical" as const,
            overflow: "hidden",
          }}>
            {chunk.paper_title}
          </p>
          {/* Authors + arXiv ID — monospace */}
          <p className="mono-label" style={{ marginTop: "2px" }}>
            {chunk.paper_authors.slice(0, 2).join(", ")}
            {chunk.paper_authors.length > 2 && " et al."}
            {" · "}arXiv:{chunk.paper_id}
          </p>
        </div>

        {/* Score badge */}
        <div style={{
          flexShrink: 0,
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: "0.68rem",
          fontWeight: 600,
          color: isWeak ? "var(--weak-match)" : "var(--cobalt)",
          padding: "3px 6px",
          border: `1px solid ${isWeak ? "var(--border-muted)" : "var(--cobalt-dim)"}`,
          borderRadius: "1px",
          lineHeight: 1,
        }}>
          {matchPercent}%
        </div>
      </div>

      {/* ── Quoted passage — italic editorial serif ── */}
      <blockquote className="evidence-card__passage">
        {passage}
      </blockquote>

      {/* ── Relevance bar ── */}
      <RelevanceBar value={chunk.score} weak={isWeak} className="my-2" />

      {/* ── Footer: arXiv link ── */}
      <div style={{ marginTop: "8px" }}>
        {linkBroken ? (
          <span className="arxiv-link arxiv-link--unavailable">
            Source link unavailable.
          </span>
        ) : (
          <a
            href={chunk.paper_pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="arxiv-link"
            onClick={(e) => {
              // Optimistically detect dead links
              if (!chunk.paper_pdf_url) {
                e.preventDefault();
                setLinkBroken(true);
              }
            }}
            style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "var(--ink-muted)" }}
          >
            View on arXiv <ExternalLink size={10} style={{ display: "inline" }} />
          </a>
        )}
      </div>
    </motion.article>
  );
}
