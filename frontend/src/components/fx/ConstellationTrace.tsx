import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

export interface TraceTarget {
  markerId: string;       // DOM id of the citation marker
  cardId: string;         // DOM id of the evidence card
  weak?: boolean;
}

interface ConstellationTraceProps {
  traces: TraceTarget[];
  activeTraceId: string | null; // markerId of the currently hovered/clicked trace
}

/**
 * ConstellationTrace — renders SVG arcs from citation markers to evidence cards.
 *
 * Architecture:
 * - A fixed full-screen SVG sits on top (pointer-events: none)
 * - Each active trace is a <path> element with animated stroke-dashoffset
 * - The path is a quadratic bezier curving through the margin whitespace
 * - Dashed variant for low-confidence (weak) citations
 */
export function ConstellationTrace({ traces, activeTraceId }: ConstellationTraceProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  // We'll update path data via a ref-based effect every render
  // (DOM measurements must happen at paint time, not during render)

  interface PathData {
    id: string;
    d: string;
    weak: boolean;
    length: number;
  }

  const pathsRef = useRef<PathData[]>([]);

  useEffect(() => {
    const measured: PathData[] = [];

    for (const trace of traces) {
      if (trace.markerId !== activeTraceId) continue;

      const markerEl = document.getElementById(trace.markerId);
      const cardEl = document.getElementById(trace.cardId);

      if (!markerEl || !cardEl) continue;

      const mRect = markerEl.getBoundingClientRect();
      const cRect = cardEl.getBoundingClientRect();

      // Start: right edge of the citation marker
      const x1 = mRect.right;
      const y1 = mRect.top + mRect.height / 2;

      // End: left edge of the evidence card, vertically centered
      const x2 = cRect.left;
      const y2 = cRect.top + cRect.height / 2;

      // Control point: pull the arc upward through the margin
      const cx = (x1 + x2) / 2;
      const cy = Math.min(y1, y2) - 40;

      const d = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;

      // Approximate path length for stroke-dasharray
      const approxLength = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * 1.3;

      measured.push({
        id: trace.markerId,
        d,
        weak: trace.weak ?? false,
        length: approxLength,
      });
    }

    pathsRef.current = measured;
  });

  const activePath = pathsRef.current.find((p) => p.id === activeTraceId);

  return (
    <svg
      ref={svgRef}
      className="constellation-svg"
      aria-hidden="true"
      style={{ width: "100vw", height: "100vh", pointerEvents: "none" }}
    >
      <AnimatePresence>
        {activePath && (
          <>
            {/* Static trace path */}
            <motion.path
              key={`trace-${activePath.id}`}
              d={activePath.d}
              fill="none"
              stroke="rgba(62, 111, 255, 0.35)"
              strokeWidth={1}
              strokeDasharray={activePath.weak ? "3 4" : "none"}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            />

            {/* Traveling bright segment — the "data flowing" signal */}
            <motion.path
              key={`signal-${activePath.id}`}
              d={activePath.d}
              fill="none"
              stroke="rgba(62, 111, 255, 0.9)"
              strokeWidth={1.5}
              strokeLinecap="round"
              strokeDasharray={`12 ${activePath.length}`}
              initial={{ strokeDashoffset: activePath.length + 12 }}
              animate={{ strokeDashoffset: -12 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.45, ease: "easeOut", delay: 0.05 }}
            />
          </>
        )}
      </AnimatePresence>
    </svg>
  );
}
