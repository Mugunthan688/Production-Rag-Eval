import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ExternalLink } from "lucide-react";
import { Badge } from "../ui/Badge";
import { ProgressRing } from "../ui/ProgressRing";
import type { ChunkData } from "../../api/client";

const springPopover = { type: "spring" as const, stiffness: 400, damping: 28 };

interface CitationPillProps {
  chunk: ChunkData;
  index: number;
}

export function CitationPill({ chunk, index }: CitationPillProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pillRef = useRef<HTMLSpanElement>(null);

  const matchPercent = Math.round(chunk.score * 100);

  return (
    <span className="relative inline-block" ref={pillRef}>
      <motion.button
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-mono font-medium bg-cyan-400/10 text-cyan-300 border border-cyan-400/25 cursor-pointer hover:bg-cyan-400/20 transition-colors"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
      >
        arXiv:{chunk.paper_id} · Chunk {index + 1}
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.95 }}
            transition={springPopover}
            className="absolute bottom-full left-0 mb-2 w-[380px] z-50 glass rounded-xl p-4 shadow-2xl border border-cyan-500/15"
            onMouseEnter={() => setIsOpen(true)}
            onMouseLeave={() => setIsOpen(false)}
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="violet">{chunk.paper_categories[0] || "cs.AI"}</Badge>
                  <span className="text-[10px] font-mono text-gray-500">arXiv:{chunk.paper_id}</span>
                </div>
                <h4 className="text-sm font-semibold text-white leading-snug line-clamp-2">
                  {chunk.paper_title}
                </h4>
                {chunk.paper_authors.length > 0 && (
                  <p className="text-[10px] text-gray-500 mt-1 truncate">
                    {chunk.paper_authors.join(", ")}
                  </p>
                )}
              </div>
              <ProgressRing value={matchPercent} size={44} label={`${matchPercent}%`} />
            </div>

            {/* Verbatim Passage */}
            <div className="bg-black/40 rounded-lg p-3 border border-white/[0.04] max-h-32 overflow-y-auto mb-3">
              <p className="text-[11px] font-mono text-gray-400 leading-relaxed">
                {chunk.text.slice(0, 300)}
                {chunk.text.length > 300 && "..."}
              </p>
            </div>

            {/* Footer */}
            <a
              href={chunk.paper_pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              Open on arXiv.org <ExternalLink size={12} />
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  );
}
