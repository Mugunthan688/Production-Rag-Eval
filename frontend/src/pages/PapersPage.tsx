import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileText, Search, ExternalLink, Tag, Calendar, Layers } from "lucide-react";
import { GlassCard } from "../components/ui/GlassCard";
import { Badge } from "../components/ui/Badge";
import { fetchPapers, fetchStats, type PaperData, type StatsData } from "../api/client";

const stagger = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const itemVariant = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 350, damping: 25 } },
};

export function PapersPage() {
  const [papers, setPapers] = useState<PaperData[]>([]);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [search, setSearch] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchPapers(), fetchStats()])
      .then(([p, s]) => {
        setPapers(p);
        setStats(s);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = papers.filter(
    (p) =>
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.id.includes(search) ||
      p.categories.some((c) => c.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="p-6 space-y-6">
      {/* Hero */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold gradient-text mb-1">📚 Paper Corpus Explorer</h1>
        <p className="text-sm text-gray-500">
          Browse and search all indexed arXiv research papers
        </p>
      </motion.div>

      {/* Stats Bar */}
      {stats && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex gap-3 flex-wrap"
        >
          <div className="glass rounded-xl px-4 py-3 flex items-center gap-2">
            <FileText size={14} className="text-cyan-400" />
            <span className="text-sm font-semibold text-white">{stats.total_papers}</span>
            <span className="text-xs text-gray-500">Papers</span>
          </div>
          <div className="glass rounded-xl px-4 py-3 flex items-center gap-2">
            <Layers size={14} className="text-violet-400" />
            <span className="text-sm font-semibold text-white">{stats.total_chunks}</span>
            <span className="text-xs text-gray-500">Chunks</span>
          </div>
          {stats.top_categories.slice(0, 4).map((cat) => (
            <div key={cat.category} className="glass rounded-xl px-3 py-3 flex items-center gap-2">
              <Tag size={12} className="text-pink-400" />
              <span className="text-xs font-mono text-gray-400">{cat.category}</span>
              <Badge variant="pink">{cat.count}</Badge>
            </div>
          ))}
        </motion.div>
      )}

      {/* Search */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
        <div className="relative max-w-md">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search papers by title, arXiv ID, or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full glass rounded-xl pl-9 pr-4 py-2.5 text-sm text-gray-200 placeholder:text-gray-600 outline-none border border-white/[0.06] focus:border-cyan-500/30 transition-colors"
          />
        </div>
      </motion.div>

      {/* Papers Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass rounded-2xl h-48 animate-pulse" />
          ))}
        </div>
      ) : (
        <motion.div
          variants={stagger}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
        >
          {filtered.map((paper) => (
            <motion.div key={paper.id} variants={itemVariant}>
              <GlassCard
                className="cursor-pointer h-full hover:border-cyan-500/20 transition-colors"
                onClick={() => setExpandedId(expandedId === paper.id ? null : paper.id)}
              >
                {/* Categories */}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  {paper.categories.slice(0, 3).map((cat) => (
                    <Badge key={cat} variant="violet">{cat}</Badge>
                  ))}
                  <Badge variant="green">{paper.chunk_count} chunks</Badge>
                </div>

                {/* Title */}
                <h3 className="text-sm font-semibold text-white leading-snug mb-2 line-clamp-2">
                  {paper.title}
                </h3>

                {/* Authors */}
                <p className="text-[11px] text-gray-500 mb-2 truncate">
                  {paper.authors.join(", ") || "Unknown authors"}
                </p>

                {/* Metadata Row */}
                <div className="flex items-center gap-3 text-[10px] text-gray-600 font-mono">
                  <span>arXiv:{paper.id}</span>
                  {paper.submitted_date && (
                    <span className="flex items-center gap-1">
                      <Calendar size={10} />
                      {paper.submitted_date.slice(0, 10)}
                    </span>
                  )}
                </div>

                {/* Expanded Abstract */}
                {expandedId === paper.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-3 pt-3 border-t border-white/[0.06]"
                  >
                    <p className="text-xs text-gray-400 leading-relaxed">{paper.abstract}</p>
                    <a
                      href={paper.pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mt-2 text-xs text-cyan-400 hover:text-cyan-300"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Open PDF <ExternalLink size={11} />
                    </a>
                  </motion.div>
                )}
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="text-center py-20">
          <p className="text-gray-500">No papers found matching "{search}"</p>
        </div>
      )}
    </div>
  );
}
