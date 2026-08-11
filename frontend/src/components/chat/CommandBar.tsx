import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { Sparkles, Send } from "lucide-react";

interface CommandBarProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

const sampleQueries = [
  "How does GraphRAG improve retrieval over flat vector search?",
  "What is Self-RAG and how does it reduce hallucination?",
  "How does Corrective RAG detect and fix retrieval errors?",
  "What role do knowledge graphs play in RAG systems?",
  "How does agentic RAG differ from standard RAG?",
];

export function CommandBar({ onSubmit, loading }: CommandBarProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 150) + "px";
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="sticky bottom-0 z-20 px-4 pb-5 pt-3">
      {/* Sample Queries */}
      {!loading && input === "" && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap gap-2 mb-3 justify-center"
        >
          {sampleQueries.slice(0, 3).map((q) => (
            <motion.button
              key={q}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setInput(q)}
              className="text-[11px] px-3 py-1.5 rounded-full glass border-white/[0.06] text-gray-400 hover:text-cyan-300 hover:border-cyan-500/20 transition-all cursor-pointer"
            >
              {q.slice(0, 55)}...
            </motion.button>
          ))}
        </motion.div>
      )}

      {/* Input Bar */}
      <motion.div
        className="max-w-3xl mx-auto glass rounded-2xl p-1.5 animate-pulse-glow border-cyan-500/10"
        layout
      >
        <div className="flex items-end gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything across your arXiv collection..."
            rows={1}
            className="flex-1 bg-transparent border-none outline-none resize-none text-sm text-gray-200 placeholder:text-gray-600 px-3 py-2.5 max-h-[150px] leading-relaxed"
          />

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleSubmit}
            disabled={!input.trim() || loading}
            className="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 flex items-center justify-center text-white disabled:opacity-30 cursor-pointer shadow-lg shadow-cyan-500/20 transition-opacity"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin-glow" />
            ) : input.trim() ? (
              <Send size={16} />
            ) : (
              <Sparkles size={16} />
            )}
          </motion.button>
        </div>
      </motion.div>

      <p className="text-center text-[10px] text-gray-600 mt-2 font-mono">
        Hybrid Dense + BM25 · Cross-Encoder Reranking · Gemini LLM
      </p>
    </div>
  );
}
