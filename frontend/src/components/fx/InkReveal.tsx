import { motion } from "framer-motion";
import { type ReactNode } from "react";

interface InkRevealProps {
  children: ReactNode;
  delay?: number;
}

/**
 * InkReveal — wraps a block of text content with a staggered reveal animation.
 * Simulates ink drying on paper: content fades in from a slightly low opacity.
 * The cobalt underline sweep effect is handled via CSS (.ink-sentence) on individual sentences.
 */
export function InkReveal({ children, delay = 0 }: InkRevealProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{
        duration: 0.5,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * InkRevealParagraph — individual paragraph with the cobalt underline sweep.
 * Each paragraph appears with a staggered delay.
 */
export function InkRevealParagraph({ children, index = 0 }: { children: ReactNode; index?: number }) {
  return (
    <motion.p
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.35,
        delay: index * 0.06,
        ease: "easeOut",
      }}
      style={{ marginBottom: "0.9em" }}
    >
      {children}
    </motion.p>
  );
}
