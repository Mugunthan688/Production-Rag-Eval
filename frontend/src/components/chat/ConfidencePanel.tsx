import { motion, AnimatePresence } from "framer-motion";
import { Shield, ShieldAlert, ShieldCheck, ChevronDown, Activity, BookOpen, Layers, Brain } from "lucide-react";
import { useState } from "react";
import type { ConfidenceReport } from "../../api/client";

interface ConfidencePanelProps {
  confidence: ConfidenceReport;
}

const riskConfig = {
  low: { icon: ShieldCheck, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "Low Risk" },
  medium: { icon: Shield, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", label: "Medium Risk" },
  high: { icon: ShieldAlert, color: "text-pink-400", bg: "bg-pink-500/10", border: "border-pink-500/20", label: "High Risk" },
};

const labelConfig = {
  HIGH: { gradient: "from-emerald-400 to-cyan-400", pulse: "animate-pulse-glow" },
  MEDIUM: { gradient: "from-amber-400 to-orange-400", pulse: "" },
  LOW: { gradient: "from-pink-400 to-red-400", pulse: "" },
};

function MetricBar({ label, value, icon: Icon, color }: { label: string; value: number; icon: typeof Activity; color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Icon size={12} className={color} />
          <span className="text-[11px] text-gray-400">{label}</span>
        </div>
        <span className="text-[11px] font-mono font-semibold text-white">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color.replace("text-", "bg-")}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(value * 100, 100)}%` }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
        />
      </div>
    </div>
  );
}

export function ConfidencePanel({ confidence }: ConfidencePanelProps) {
  const [expanded, setExpanded] = useState(false);
  const risk = riskConfig[confidence.hallucination_risk];
  const label = labelConfig[confidence.confidence_label];
  const RiskIcon = risk.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className={`rounded-xl border ${risk.border} ${risk.bg} overflow-hidden`}
    >
      {/* Header — always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2.5 cursor-pointer hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-2">
          <RiskIcon size={16} className={risk.color} />
          <span className="text-xs font-semibold text-gray-300">Confidence</span>
          <span className={`text-xs font-bold font-mono bg-gradient-to-r ${label.gradient} bg-clip-text text-transparent`}>
            {confidence.confidence_label}
          </span>
          <span className="text-[10px] font-mono text-gray-500">
            ({(confidence.composite_confidence * 100).toFixed(0)}%)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] px-2 py-0.5 rounded-full border ${risk.border} ${risk.color} font-medium`}>
            {risk.label}
          </span>
          <motion.div
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown size={14} className="text-gray-500" />
          </motion.div>
        </div>
      </button>

      {/* Expanded details */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 space-y-3 border-t border-white/[0.04]">
              {/* Metric bars */}
              <div className="pt-3 space-y-2.5">
                <MetricBar
                  label="Retrieval Confidence"
                  value={confidence.retrieval_confidence}
                  icon={Activity}
                  color="text-cyan-400"
                />
                <MetricBar
                  label="Source Diversity"
                  value={confidence.source_diversity}
                  icon={Layers}
                  color="text-violet-400"
                />
                <MetricBar
                  label="Answer Grounding"
                  value={confidence.answer_grounding}
                  icon={BookOpen}
                  color="text-emerald-400"
                />
                <MetricBar
                  label="Score Entropy"
                  value={confidence.score_distribution.normalized_entropy}
                  icon={Brain}
                  color="text-pink-400"
                />
              </div>

              {/* Explanation */}
              <div className="rounded-lg bg-white/[0.02] border border-white/[0.04] px-3 py-2">
                <p className="text-[11px] text-gray-400 leading-relaxed">
                  {confidence.explanation}
                </p>
              </div>

              {/* Score distribution stats */}
              <div className="grid grid-cols-3 gap-2">
                <div className="text-center p-1.5 rounded-md bg-white/[0.02]">
                  <p className="text-[10px] font-mono font-bold text-white">{confidence.score_distribution.mean.toFixed(3)}</p>
                  <p className="text-[9px] text-gray-600">Mean Score</p>
                </div>
                <div className="text-center p-1.5 rounded-md bg-white/[0.02]">
                  <p className="text-[10px] font-mono font-bold text-white">{confidence.score_distribution.top1_gap.toFixed(3)}</p>
                  <p className="text-[9px] text-gray-600">Top-1 Gap</p>
                </div>
                <div className="text-center p-1.5 rounded-md bg-white/[0.02]">
                  <p className="text-[10px] font-mono font-bold text-white">{confidence.score_distribution.std.toFixed(3)}</p>
                  <p className="text-[9px] text-gray-600">Score StdDev</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
