import { motion } from "framer-motion";
import { Cpu, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ThinkingAccordion } from "./ThinkingAccordion";
import { CitationPill } from "./CitationPopover";
import { ConfidencePanel } from "./ConfidencePanel";
import { Badge } from "../ui/Badge";
import type { ChunkData, ConfidenceReport } from "../../api/client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  chunks?: ChunkData[];
  latencyMs?: number;
  papersSearched?: number;
  confidence?: ConfidenceReport;
}

export function ChatMessage({ role, content, chunks, latencyMs, papersSearched, confidence }: ChatMessageProps) {
  const isUser = role === "user";

  // Build thinking steps from chunks
  const thinkingSteps = chunks
    ? [
        { text: `Searching vector embeddings across ${papersSearched ?? 0} indexed papers...`, status: "done" as const },
        ...chunks.slice(0, 3).map((c) => ({
          text: `Retrieved chunk from arXiv:${c.paper_id} (${(c.score * 100).toFixed(1)}% match)`,
          status: "done" as const,
        })),
        { text: `Synthesizing grounded response from ${chunks.length} context chunks...`, status: "done" as const },
      ]
    : [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98, y: 12 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 350, damping: 25 }}
      className={`flex gap-4 ${isUser ? "justify-end" : ""}`}
    >
      {/* Avatar */}
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 mt-1">
          <Cpu size={14} className="text-white" />
        </div>
      )}

      <div className={`flex-1 max-w-[85%] ${isUser ? "flex flex-col items-end" : ""}`}>
        {/* User Message */}
        {isUser && (
          <div className="glass rounded-2xl rounded-tr-md px-4 py-3 max-w-lg border-violet-500/20">
            <p className="text-sm text-gray-200">{content}</p>
          </div>
        )}

        {/* AI Response */}
        {!isUser && (
          <div className="space-y-3">
            {/* Thinking Accordion */}
            {chunks && chunks.length > 0 && (
              <ThinkingAccordion steps={thinkingSteps} papersSearched={papersSearched ?? 0} />
            )}

            {/* Answer Content */}
            <div className="glass rounded-2xl rounded-tl-md px-5 py-4 border-cyan-500/10">
              {/* Latency badge */}
              {latencyMs !== undefined && (
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant="green">{latencyMs.toFixed(0)}ms</Badge>
                  <Badge variant="cyan">{chunks?.length ?? 0} chunks</Badge>
                </div>
              )}

              {/* Markdown Content */}
              <div className="prose prose-invert prose-sm max-w-none text-gray-300 leading-relaxed [&_p]:mb-3 [&_ul]:mb-3 [&_ol]:mb-3 [&_h1]:gradient-text [&_h2]:gradient-text [&_h3]:text-cyan-300 [&_strong]:text-white [&_code]:bg-white/[0.06] [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:font-mono [&_code]:text-cyan-300 [&_a]:text-cyan-400">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
              </div>

              {/* Confidence Panel */}
              {confidence && (
                <div className="mt-3">
                  <ConfidencePanel confidence={confidence} />
                </div>
              )}

              {/* Citation Pills */}
              {chunks && chunks.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/[0.06]">
                  <p className="text-[10px] font-mono text-gray-500 mb-2 uppercase tracking-wider">
                    Sources
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {chunks.map((chunk, i) => (
                      <CitationPill key={chunk.chunk_id} chunk={chunk} index={i} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-xl bg-white/[0.06] border border-white/[0.1] flex items-center justify-center mt-1">
          <User size={14} className="text-gray-400" />
        </div>
      )}
    </motion.div>
  );
}
