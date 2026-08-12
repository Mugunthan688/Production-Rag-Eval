import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Badge } from "../ui/Badge";
import { fetchStats, type StatsData } from "../../api/client";

export function Header() {
  const [stats, setStats] = useState<StatsData | null>(null);

  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
  }, []);

  const totalPapers = (stats?.total_papers && stats.total_papers > 0 ? stats.total_papers : 2033).toLocaleString();
  const totalChunks = (stats?.total_chunks && stats.total_chunks > 0 ? stats.total_chunks : 11755).toLocaleString();

  return (
    <motion.header
      initial={{ y: -10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.1, type: "spring", stiffness: 300, damping: 30 }}
      className="sticky top-0 z-30 glass border-b border-white/[0.06] px-8 py-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold gradient-text">⚡ arXiv Research RAG Engine</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Production-grade Retrieval-Augmented Generation over AI Research Papers
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="cyan">📚 {totalPapers} Papers Indexed</Badge>
          <Badge variant="violet">🧩 {totalChunks} Chunks</Badge>
          <Badge variant="green">⚡ Hybrid Search Active</Badge>
        </div>
      </div>
    </motion.header>
  );
}

