import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import { MessageSquare, FileText, FlaskConical, MessageCircle, Cpu } from "lucide-react";

const navItems = [
  { to: "/", icon: MessageSquare, label: "Chat Workspace" },
  { to: "/papers", icon: FileText, label: "Paper Explorer" },
  { to: "/experiments", icon: FlaskConical, label: "Experiments" },
  { to: "/feedback", icon: MessageCircle, label: "Feedback" },
];

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="fixed left-0 top-0 bottom-0 w-64 glass border-r border-white/[0.06] z-40 flex flex-col"
    >
      {/* Logo */}
      <div className="p-6 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">Deep Research AI</h1>
            <p className="text-[10px] font-mono text-cyan-400/80 tracking-wider">arXiv Research Engine</p>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-5 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent" />

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-white/[0.06] text-cyan-300 border border-cyan-500/20 shadow-lg shadow-cyan-500/5"
                  : "text-gray-400 hover:text-gray-200 hover:bg-white/[0.03]"
              }`
            }
          >
            <item.icon size={16} className="shrink-0" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/[0.04]">
        <p className="text-[10px] font-mono text-gray-600 text-center">
          arXiv RAG v0.1.0
        </p>
      </div>
    </motion.aside>
  );
}
