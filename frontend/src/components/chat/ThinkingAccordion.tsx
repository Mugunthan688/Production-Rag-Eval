import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

interface ThinkingStep {
  text: string;
  status: "done" | "active";
}

interface ThinkingAccordionProps {
  steps: ThinkingStep[];
  papersSearched: number;
}

export function ThinkingAccordion({ steps, papersSearched }: ThinkingAccordionProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div layout className="glass rounded-xl overflow-hidden mb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 text-left cursor-pointer hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-cyan-400 text-xs">✦</span>
          <span className="text-xs font-medium text-gray-400">
            Retrieval pipeline — searched {papersSearched} papers
          </span>
        </div>
        <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={14} className="text-gray-500" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 space-y-2 border-t border-white/[0.04]">
              {steps.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08, type: "spring", stiffness: 350, damping: 25 }}
                  className="flex items-start gap-2 pt-2"
                >
                  <span className={step.status === "done" ? "text-emerald-400" : "text-cyan-400"}>
                    {step.status === "done" ? "✓" : "✦"}
                  </span>
                  <span className="text-xs text-gray-400 font-mono leading-relaxed">
                    {step.text}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
