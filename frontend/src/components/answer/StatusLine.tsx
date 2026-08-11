import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface StatusLineProps {
  active: boolean;
}

const STATUS_CYCLE = ["RETRIEVING", "RANKING", "SYNTHESIZING"] as const;
type StatusLabel = (typeof STATUS_CYCLE)[number];

/**
 * StatusLine — appears in the query bar's bottom hairline during loading.
 * Cycles monospace uppercase status labels with 150ms crossfades.
 * Never a spinner.
 */
export function StatusLine({ active }: StatusLineProps) {
  const [statusIdx, setStatusIdx] = useState(0);

  useEffect(() => {
    if (!active) {
      setStatusIdx(0);
      return;
    }

    // Advance through RETRIEVING → RANKING → SYNTHESIZING
    const intervals = [900, 1600, Infinity]; // ms before moving to next
    let current = 0;

    const advance = () => {
      current++;
      if (current < STATUS_CYCLE.length) {
        setStatusIdx(current);
        if (intervals[current] !== Infinity) {
          setTimeout(advance, intervals[current]);
        }
      }
    };

    const first = setTimeout(advance, intervals[0]);
    return () => clearTimeout(first);
  }, [active]);

  const label: StatusLabel = STATUS_CYCLE[Math.min(statusIdx, STATUS_CYCLE.length - 1)];

  if (!active) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: "20px",
        display: "flex",
        alignItems: "center",
        paddingLeft: "14px",
        overflow: "hidden",
      }}
    >
      {/* Indeterminate cobalt progress line */}
      <div className="query-bar__progress" style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: "1px" }}>
        <div className="query-bar__progress-fill" />
      </div>

      {/* Status label crossfade */}
      <AnimatePresence mode="wait">
        <motion.span
          key={label}
          className="status-text"
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
        >
          {label}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
