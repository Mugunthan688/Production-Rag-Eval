import { motion, AnimatePresence } from "framer-motion";
import { EvidenceCard } from "./EvidenceCard";
import type { ChunkData } from "../../api/client";

interface EvidenceRailProps {
  chunks: ChunkData[];
  highlightedChunkId: string | null;
  onHighlight: (chunkId: string | null) => void;
}

/**
 * EvidenceRail — the right column.
 * Stacked Evidence Cards replacing PDFs as the source visualization.
 * This rail is a first-class, emotionally central object.
 */
export function EvidenceRail({ chunks, highlightedChunkId, onHighlight }: EvidenceRailProps) {
  return (
    <aside
      id="evidence-rail"
      style={{
        width: "288px",
        minWidth: "288px",
        height: "calc(100vh - 0px)",
        overflowY: "auto",
        overflowX: "hidden",
        borderLeft: "1px solid var(--border)",
        backgroundColor: "var(--canvas)",
        padding: "20px 14px 80px 14px",
        position: "relative",
        zIndex: 10,
      }}
    >
      {/* Rail Header */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "16px",
        paddingBottom: "10px",
        borderBottom: "1px solid var(--border)",
      }}>
        <span className="mono-label" style={{ fontSize: "0.6rem", letterSpacing: "0.14em" }}>
          Evidence
        </span>
        {chunks.length > 0 && (
          <span className="mono-label" style={{ color: "var(--cobalt)", fontSize: "0.6rem" }}>
            {chunks.length} source{chunks.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      <AnimatePresence mode="popLayout">
        {chunks.length === 0 ? (
          /* Empty state placeholder card */
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="evidence-card"
            style={{ textAlign: "center", padding: "24px 14px" }}
          >
            <p className="mono-label" style={{ marginBottom: "6px", fontSize: "0.58rem" }}>
              No sources to trace.
            </p>
            <p style={{
              fontFamily: "'Fraunces', Georgia, serif",
              fontSize: "0.78rem",
              color: "var(--ink-faint)",
              fontStyle: "italic",
              lineHeight: 1.5,
            }}>
              Ask a question — evidence will appear here as index cards drawn from the corpus.
            </p>
          </motion.div>
        ) : (
          chunks.map((chunk, i) => (
            <EvidenceCard
              key={chunk.chunk_id}
              chunk={chunk}
              index={i}
              isHighlighted={highlightedChunkId === chunk.chunk_id}
              onHighlight={onHighlight}
            />
          ))
        )}
      </AnimatePresence>
    </aside>
  );
}
