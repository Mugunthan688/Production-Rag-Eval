import { useEffect, useRef, useState } from "react";

interface CitationMarkerProps {
  index: number;           // 1-based citation number
  chunkId: string;         // links to the evidence card DOM id
  onActivate: (chunkId: string | null) => void;
  activeChunkId: string | null;
}

/**
 * CitationMarker — inline [n] superscript that links to an EvidenceCard.
 *
 * On first render: orange pulse ring (citationPulse animation).
 * On hover/click: activates the ConstellationTrace to the matching card.
 * Color: cobalt (--cobalt) — reserved for RAG system voice, never orange.
 */
export function CitationMarker({ index, chunkId, onActivate, activeChunkId }: CitationMarkerProps) {
  const [hasPulsed, setHasPulsed] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);
  const isActive = activeChunkId === chunkId;

  // Fire the pulse animation once on mount
  useEffect(() => {
    const t = setTimeout(() => setHasPulsed(true), 800 + index * 150);
    return () => clearTimeout(t);
  }, [index]);

  return (
    <span
      id={`citation-marker-${chunkId}`}
      ref={ref}
      className={`citation-marker ${!hasPulsed ? "citation-marker--new" : ""}`}
      style={{
        background: isActive ? "var(--cobalt-dim)" : "transparent",
        borderColor: isActive ? "var(--cobalt)" : "var(--cobalt-dim)",
        cursor: "pointer",
      }}
      title={`Source ${index}`}
      role="button"
      aria-label={`Citation ${index}`}
      tabIndex={0}
      onMouseEnter={() => onActivate(chunkId)}
      onMouseLeave={() => onActivate(null)}
      onClick={() => onActivate(isActive ? null : chunkId)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onActivate(isActive ? null : chunkId);
        }
      }}
    >
      {index}
    </span>
  );
}
