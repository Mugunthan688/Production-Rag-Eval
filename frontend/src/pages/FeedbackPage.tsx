import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { MessageCircle, ThumbsUp, ThumbsDown, AlertTriangle } from "lucide-react";
import { GlassCard } from "../components/ui/GlassCard";
import { Badge } from "../components/ui/Badge";
import { fetchFeedbackAnalytics, type FeedbackAnalytics } from "../api/client";

export function FeedbackPage() {
  const [data, setData] = useState<FeedbackAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFeedbackAnalytics()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold gradient-text mb-1">💬 Feedback Analytics</h1>
        <p className="text-sm text-gray-500">
          Review user ratings, low-scoring queries, and problematic chunks
        </p>
      </motion.div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="glass rounded-2xl h-24 animate-pulse" />
          ))}
        </div>
      ) : data && data.lowest_rated_queries.length > 0 ? (
        <div className="space-y-4">
          {data.lowest_rated_queries.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08, type: "spring", stiffness: 350, damping: 25 }}
            >
              <GlassCard>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={item.rating > 0 ? "green" : "pink"}>
                        {item.rating > 0 ? (
                          <><ThumbsUp size={10} /> +1</>
                        ) : (
                          <><ThumbsDown size={10} /> -1</>
                        )}
                      </Badge>
                      <span className="text-[10px] font-mono text-gray-600">
                        Feedback #{item.id}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-white mb-1 truncate">{item.query}</p>
                    <p className="text-xs text-gray-500 line-clamp-2">{item.answer}</p>
                    {item.comments && (
                      <p className="text-xs text-amber-400/80 mt-2 italic">"{item.comments}"</p>
                    )}
                  </div>
                  <div className="shrink-0">
                    {item.rating > 0 ? (
                      <ThumbsUp size={16} className="text-emerald-400" />
                    ) : (
                      <ThumbsDown size={16} className="text-pink-400" />
                    )}
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center py-20 text-center"
        >
          <div className="w-14 h-14 rounded-2xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center mb-4">
            <MessageCircle size={24} className="text-gray-600" />
          </div>
          <h3 className="text-sm font-semibold text-gray-400 mb-1">No Feedback Yet</h3>
          <p className="text-xs text-gray-600 max-w-sm">
            Submit feedback on query results in the Chat Workspace to see analytics here.
          </p>
        </motion.div>
      )}

      {/* Info Card */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="glass rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle size={14} className="text-amber-400" />
          <h4 className="text-xs font-semibold text-gray-300">Feedback Collection</h4>
        </div>
        <p className="text-xs text-gray-500 leading-relaxed">
          Each query in the Chat Workspace can be rated with 👍 (+1) or 👎 (-1).
          Low-rated queries are surfaced here for continuous improvement of the
          retrieval pipeline and answer quality.
        </p>
      </motion.div>
    </div>
  );
}
