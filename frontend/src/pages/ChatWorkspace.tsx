import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { ChatMessage } from "../components/chat/ChatMessage";
import { CommandBar } from "../components/chat/CommandBar";
import { ShimmerBlock } from "../components/ui/Shimmer";
import { executeQuery, type QueryResponse, type ChunkData, type ConfidenceReport } from "../api/client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  chunks?: ChunkData[];
  latencyMs?: number;
  papersSearched?: number;
  confidence?: ConfidenceReport;
}

export function ChatWorkspace() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (query: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: query,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data: QueryResponse = await executeQuery({ query });

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        chunks: data.chunks_used,
        latencyMs: data.latency_ms,
        papersSearched: data.papers_searched,
        confidence: data.confidence,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `**Error**: Could not connect to the API server. Make sure the FastAPI backend is running at \`http://localhost:8000\`.\n\n\`\`\`\n${err}\n\`\`\``,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-73px)]">
      {/* Chat Feed */}
      <div ref={feedRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex flex-col items-center justify-center h-full text-center"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400/20 to-violet-500/20 flex items-center justify-center mb-6 animate-float border border-cyan-500/10">
              <span className="text-3xl">⚡</span>
            </div>
            <h2 className="text-2xl font-bold gradient-text mb-2">
              Deep Research RAG Engine
            </h2>
            <p className="text-sm text-gray-500 max-w-md leading-relaxed">
              Ask any research question across your indexed arXiv paper corpus.
              Multi-strategy retrieval with neural reranking and grounded LLM generation.
            </p>
            <div className="flex gap-2 mt-6">
              {["GraphRAG", "Self-RAG", "CRAG", "Agentic RAG", "Long-Context"].map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] font-mono px-2 py-1 rounded-full bg-white/[0.03] border border-white/[0.06] text-gray-500"
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            role={msg.role}
            content={msg.content}
            chunks={msg.chunks}
            latencyMs={msg.latencyMs}
            papersSearched={msg.papersSearched}
            confidence={msg.confidence}
          />
        ))}

        {loading && (
          <div className="flex gap-4">
            <div className="shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center animate-pulse">
              <span className="text-white text-xs">⚡</span>
            </div>
            <div className="flex-1 max-w-[85%] glass rounded-2xl">
              <ShimmerBlock />
            </div>
          </div>
        )}
      </div>

      {/* Command Bar */}
      <CommandBar onSubmit={handleSubmit} loading={loading} />
    </div>
  );
}
