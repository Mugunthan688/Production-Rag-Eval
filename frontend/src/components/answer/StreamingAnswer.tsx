import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import { InkReveal } from "../fx/InkReveal";
import { CitationMarker } from "./CitationMarker";
import type { ChunkData, ConfidenceReport } from "../../api/client";

interface StreamingAnswerProps {
  content: string;
  chunks: ChunkData[];
  latencyMs?: number;
  papersSearched?: number;
  confidence?: ConfidenceReport;
  activeChunkId: string | null;
  onActivateCitation: (chunkId: string | null) => void;
}

const WEAK_THRESHOLD = 0.55;

/**
 * StreamingAnswer — renders the RAG answer in editorial serif (Fraunces).
 *
 * Citation markers [n] are rendered as interactive CitationMarker spans.
 * Low-confidence retrieval shows a quiet monospace warning line above the answer.
 */
export function StreamingAnswer({
  content,
  chunks,
  latencyMs,
  papersSearched,
  confidence,
  activeChunkId,
  onActivateCitation,
}: StreamingAnswerProps) {
  const allWeak = chunks.length > 0 && chunks.every((c) => c.score < WEAK_THRESHOLD);
  const hasWeakEvidence = confidence && confidence.composite_confidence < 0.45;

  // Build a lookup: citation number → chunk (by position in chunks array)
  const chunkByIndex = useMemo(() => {
    const map = new Map<number, ChunkData>();
    chunks.forEach((c, i) => map.set(i + 1, c));
    return map;
  }, [chunks]);

  return (
    <InkReveal>
      {/* Low-confidence warning line */}
      {(allWeak || hasWeakEvidence) && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mono-label"
          style={{
            fontSize: "0.62rem",
            marginBottom: "14px",
            letterSpacing: "0.09em",
            color: "var(--ink-faint)",
          }}
        >
          Limited supporting evidence found in the corpus for this query.
        </motion.p>
      )}

      {/* Answer in editorial serif */}
      <div className="answer-text">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // Intercept inline code to detect citation markers like `[1]`
            // Actually we process citation markers via text parsing below
            p: ({ children }) => <p>{children}</p>,
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
            ),
            // Render inline text — intercept [n] patterns
            // ReactMarkdown renders text nodes, we handle via the wrapper approach
          }}
        >
          {/* Pre-process content: replace [1], [2] with placeholder spans */}
          {content.replace(/\[(\d+)\]/g, (_, n) => `\`[${n}]\``)}
        </ReactMarkdown>
      </div>

      {/* Interactive Evidence Pills Toolbar — shown below answer text */}
      {chunks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.35 }}
          style={{
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: "8px",
            marginTop: "16px",
            paddingTop: "12px",
            borderTop: "1px solid var(--border)",
          }}
        >
          <span className="mono-label" style={{ fontSize: "0.58rem" }}>
            Interactive Evidence:
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            {chunks.map((chunk, i) => (
              <CitationMarker
                key={chunk.chunk_id}
                index={i + 1}
                chunkId={chunk.chunk_id}
                activeChunkId={activeChunkId}
                onActivate={onActivateCitation}
              />
            ))}
          </div>
          {chunkByIndex.size > 0 && (
            <span className="mono-label" style={{ marginLeft: "8px", fontSize: "0.58rem" }}>
              ({papersSearched} paper{papersSearched !== 1 ? "s" : ""} searched
              {latencyMs !== undefined ? ` · ${latencyMs.toFixed(0)}ms` : ""})
            </span>
          )}
        </motion.div>
      )}

      {/* Confidence annotation — quiet, monospace */}
      {confidence && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.45 }}
          style={{
            marginTop: "10px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span className="mono-label" style={{ fontSize: "0.58rem" }}>
            Confidence
          </span>
          <span className="mono-label" style={{
            color: confidence.confidence_label === "HIGH"
              ? "var(--cobalt)"
              : confidence.confidence_label === "MEDIUM"
                ? "var(--ink-muted)"
                : "var(--weak-match)",
            fontSize: "0.58rem",
          }}>
            {confidence.confidence_label}
          </span>
          <span className="mono-label" style={{ fontSize: "0.55rem", color: "var(--ink-faint)" }}>
            {(confidence.composite_confidence * 100).toFixed(0)}%
            · {confidence.hallucination_risk} hallucination risk
          </span>
        </motion.div>
      )}
    </InkReveal>
  );
}
