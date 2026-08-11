import { motion } from "framer-motion";

interface RelevanceBarProps {
  value: number; // 0–1
  weak?: boolean;
  className?: string;
}

/**
 * A thin horizontal bar that fills with cobalt (or gray for weak matches).
 * Uses a slight overshoot bounce — not linear.
 */
export function RelevanceBar({ value, weak = false, className = "" }: RelevanceBarProps) {
  const clampedValue = Math.max(0, Math.min(1, value));

  return (
    <div className={`relevance-bar ${className}`} role="meter" aria-valuenow={Math.round(clampedValue * 100)} aria-valuemin={0} aria-valuemax={100}>
      <motion.div
        className={`relevance-bar__fill ${weak ? "relevance-bar__fill--weak" : ""}`}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: clampedValue }}
        transition={{
          type: "spring",
          stiffness: 220,
          damping: 18,
          mass: 0.8,
          delay: 0.1,
        }}
        style={{ transformOrigin: "left center" }}
      />
    </div>
  );
}
